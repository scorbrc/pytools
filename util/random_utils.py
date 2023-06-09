""" Random utility tools. """
import datetime as dt
from random import choice, choices, random, randint, sample, shuffle
from string import digits, ascii_lowercase, ascii_uppercase
from time import time
from util.time_utils import to_utc


# Base 36 characters.
B36_CHARS = digits + ascii_uppercase

# Base 62 characters.
B62_CHARS = digits + ascii_lowercase + ascii_uppercase

# Character classes for random composite words.
RANDOM_COMP_CHARS = \
    (digits,
     ascii_uppercase,
     ascii_lowercase,
     '!#$%&*+=?@~^')


# General words organized into types.
WORDS = \
  (('bear', 'beaver', 'bird', 'bison', 'camel', 'cat', 'chipmonk',
    'cougar', 'cow', 'coyote', 'deer', 'dog', 'donkey', 'duck',
    'elephant', 'elk', 'fish', 'fox', 'frog', 'goat', 'horse', 'lion',
    'lizzard', 'mole', 'monkey', 'moose', 'mouse', 'pig', 'rhino',
    'sheep', 'snake', 'tiger', 'toad', 'wolf', 'zebra'),
   ('cardinal', 'crow', 'dove', 'duck', 'eagle', 'falcon', 'finch',
    'goose', 'gull', 'hawk', 'heron', 'lark', 'loon', 'owl', 'parrot',
    'penguin', 'robin', 'raven', 'sparrow', 'swallow', 'swan', 'tern',
    'turkey', 'wren'),
   ('apple', 'apricot', 'banana', 'blueberry', 'blackberry', 'cherry',
    'bean', 'corn', 'fig', 'grape', 'honey', 'kiwi', 'lemon', 'lime',
    'mango', 'melon', 'nectar', 'pea', 'peach', 'plum', 'potato',
    'squash', 'tomato', 'watermelon'),
   ('amber', 'aqua', 'auburn', 'azure', 'beige', 'black', 'blue',
    'bronze', 'brown', 'coral', 'crimson', 'cyan', 'gold', 'gray',
    'green', 'ivory', 'lava', 'lime', 'magenta', 'maroon', 'olive',
    'orange', 'pink', 'purple', 'red', 'rose', 'silver', 'tan', 'teal',
    'voilet', 'white', 'yellow'),
   ('brook', 'bucolic', 'burn', 'bush', 'cliff', 'creek', 'field',
    'forest', 'glade', 'glen', 'hill', 'land', 'mountain', 'pastoral',
    'path', 'plain', 'plant', 'rise', 'road', 'rock', 'rural', 'rustic',
    'stick', 'stone', 'stream', 'trail', 'tree', 'valley'),
   ('after', 'ahead', 'around', 'around', 'before', 'east', 'left',
    'over', 'passing', 'north', 'right', 'south', 'straight', 'under', 'west'),
   ('balcony', 'batten', 'beam', 'casing', 'ceiling', 'closet',
    'cottage', 'door', 'dormer', 'eaves', 'floor', 'footing',
    'fountain', 'gable', 'garden', 'hall', 'hearth', 'house', 'joist',
    'kitchen', 'landing', 'pillar', 'porch', 'rafter', 'rail', 'step',
    'stud', 'wall', 'window', 'yard'),
   ('big', 'flat', 'grand', 'great', 'huge', 'large', 'long', 'mammoth',
    'massive', 'medium', 'short', 'small', 'tall', 'tiny'),
   ('brave', 'eager', 'faithful', 'gentle', 'happy', 'jolly', 'kind',
    'loud', 'nice', 'proud', 'quiet', 'vain'),
   ('bright', 'clean', 'clear', 'dour', 'elegant', 'fancy', 'good',
    'shapely', 'sharp', 'slim', 'smart', 'smooth', 'strange', 'shade', 'sun'),
   ('arrow', 'circle', 'crescent', 'cross', 'cube', 'cylinder',
    'eliptical', 'heart', 'hexagon', 'line', 'octagon', 'oval',
    'parallel', 'pentagon', 'point', 'square', 'star', 'triangle'),
   ('baker', 'blazer', 'builder', 'charter', 'craft', 'dancer', 'driver',
    'farmer', 'fisher', 'foreman', 'founder', 'gardener', 'hunter',
    'leader', 'mechanic', 'pilot', 'plumber', 'potter', 'seeker'),
   ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
    'eight', 'nine', 'ten', 'eleven', 'twelve'),
   ('adorable', 'adventurous', 'aggressive', 'agreeable', 'alert',
    'alive', 'amused', 'attractive', 'average', 'beautiful',
    'better', 'bewildered', 'black', 'bloody', 'blue', 'brainy',
    'brave', 'bright', 'busy', 'calm', 'careful', 'cautious',
    'charming', 'cheerful', 'clean', 'clear', 'clever', 'cloudy',
    'clumsy', 'colorful', 'comfortable', 'cooperative', 'courageous',
    'crazy', 'crowded', 'curious', 'cute', 'defiant', 'delightful',
    'determined', 'distinct', 'doubtful', 'eager', 'easy', 'elated',
    'elegant', 'enchanting', 'encouraging', 'energetic',
    'enthusiastic', 'envious', 'excited', 'expensive', 'exuberant',
    'fair', 'faithful', 'famous', 'fancy', 'fantastic', 'fine',
    'friendly', 'frightened', 'funny', 'gentle', 'gifted', 'glamorous',
    'gleaming', 'glorious', 'good', 'gorgeous', 'graceful', 'handsome',
    'happy', 'healthy', 'helpful', 'hilarious', 'horrible', 'hungry',
    'important', 'innocent', 'inquisitive', 'jolly', 'joyous', 'kind',
    'lazy', 'light', 'lively', 'lonely', 'long', 'lovely',
    'lucky', 'magnificent', 'misty', 'modern', 'motionless',
    'muddy', 'mushy', 'mysterious', 'nice', 'obedient', 'perfect',
    'plain', 'pleasant', 'poised', 'poor', 'powerful', 'precious',
    'prickly', 'proud', 'quaint', 'real', 'relieved', 'rich', 'scary',
    'selfish', 'shiny', 'shy', 'silly', 'sleepy', 'smiling',
    'sparkling', 'splendid', 'spotless', 'stormy', 'strange',
    'successful', 'super', 'talented', 'tame', 'tasty', 'tender',
    'tense', 'thankful', 'thoughtful', 'tough', 'vast', 'victorious',
    'vivacious', 'wandering', 'weary', 'wicked', 'wild'))

CITIES_AND_TOWNS = \
   ('Abilene', 'Akron', 'Albuquerque', 'Alexandria', 'Allen', 'Allentown',
    'Amarillo', 'Anaheim', 'Anchorage', 'Ann Arbor', 'Antioch', 'Arlington',
    'Arvada', 'Athens', 'Atlanta', 'Augusta', 'Aurora', 'Austin', 'Bakersfield',
    'Baltimore', 'Baton Rouge', 'Beaumont', 'Bellevue', 'Bend', 'Berkeley',
    'Billings', 'Birmingham', 'Boise', 'Boston', 'Bridgeport', 'Broken Arrow',
    'Brownsville', 'Buckeye', 'Buffalo', 'Cambridge', 'Cape Coral', 'Carlsbad',
    'Carrollton', 'Cary', 'Cedar Rapids', 'Chandler', 'Charleston', 'Charlotte',
    'Chattanooga', 'Chesapeake', 'Chicago', 'Chula Vista', 'Cincinnati',
    'Clarksville', 'Clearwater', 'Cleveland', 'Clovis', 'College Station',
    'Colorado Springs', 'Columbia', 'Columbus', 'Concord', 'Coral Springs',
    'Corona', 'Corpus Christi', 'Costa Mesa', 'Dallas', 'Dayton', 'Dearborn',
    'Denton', 'Denver', 'Des Moines', 'Detroit', 'Downey', 'Durham',
    'Edinburg', 'El Paso', 'Elgin', 'Elizabeth', 'Elk Grove', 'Escondido',
    'Eugene', 'Evansville', 'Everett', 'Fairfield', 'Fargo', 'Fayetteville',
    'Fontana', 'Fort Collins', 'Fort Lauderdale', 'Fort Myers', 'Fort Wayne',
    'Fort Worth', 'Fremont', 'Fresno', 'Frisco', 'Fullerton', 'Gainesville',
    'Garden Grove', 'Garland', 'Gilbert', 'Glendale', 'Goodyear',
    'Grand Prairie', 'Grand Rapids', 'Greeley', 'Green Bay', 'Greensboro',
    'Gresham', 'Hampton', 'Hartford', 'Hayward', 'Henderson', 'Hialeah',
    'High Point', 'Hillsboro', 'Hollywood', 'Honolulu', 'Houston',
    'Huntington Beach', 'Huntsville', 'Independence', 'Indianapolis',
    'Irvine', 'Irving', 'Jackson', 'Jacksonville', 'Jersey City', 'Joliet',
    'Kansas City', 'Kent', 'Killeen', 'Knoxville', 'Lafayette', 'Lakeland',
    'Lakewood', 'Lancaster', 'Lansing', 'Laredo', 'Las Cruces', 'Las Vegas',
    'League City', 'Lewisville', 'Lexington', 'Lincoln', 'Little Rock',
    'Long Beach', 'Los Angeles', 'Louisville', 'Lowell', 'Lubbock',
    'Madison', 'Manchester', 'McAllen', 'McKinney', 'Memphis', 'Menifee',
    'Meridian', 'Mesa', 'Mesquite', 'Miami', 'Miami Gardens', 'Midland',
    'Milwaukee', 'Minneapolis', 'Miramar', 'Mobile', 'Modesto', 'Montgomery',
    'Moreno Valley', 'Murfreesboro', 'Murrieta', 'Nampa', 'Naperville',
    'Nashville', 'New Braunfels', 'New Haven', 'New Orleans', 'New York City',
    'Newark', 'Newport News', 'Norfolk', 'Norman', 'North Charleston',
    'North Las Vegas', 'Oakland', 'Oceanside', 'Odessa', 'Oklahoma City',
    'Olathe', 'Omaha', 'Ontario', 'Orange', 'Orlando', 'Overland Park',
    'Oxnard', 'Palm Bay', 'Palmdale', 'Pasadena', 'Paterson', 'Pearland',
    'Pembroke Pines', 'Peoria', 'Philadelphia', 'Phoenix', 'Pittsburgh',
    'Plano', 'Pomona', 'Pompano Beach', 'Port St. Lucie', 'Portland',
    'Providence', 'Provo', 'Pueblo', 'Raleigh', 'Rancho Cucamonga', 'Reno',
    'Richardson', 'Richmond', 'Rio Rancho', 'Riverside', 'Rochester',
    'Rockford', 'Roseville', 'Round Rock', 'Sacramento', 'Salem', 'Salinas',
    'Salt Lake City', 'San Antonio', 'San Bernardino', 'San Diego',
    'San Francisco', 'San Jose', 'Sandy Springs', 'Santa Ana', 'Santa Clara',
    'Santa Clarita', 'Santa Maria', 'Santa Rosa', 'Savannah', 'Scottsdale',
    'Seattle', 'Shreveport', 'Simi Valley', 'Sioux Falls', 'Sparks', 'Spokane',
    'Spokane Valley', 'Springfield', 'St. George', 'St. Louis', 'St. Paul',
    'St. Petersburg', 'Stamford', 'Sterling Heights', 'Stockton', 'Sugar Land',
    'Sunnyvale', 'Surprise', 'Syracuse', 'Tacoma', 'Tallahassee', 'Tampa',
    'Temecula', 'Tempe', 'Thornton', 'Thousand Oaks', 'Toledo', 'Topeka',
    'Torrance', 'Tucson', 'Tulsa', 'Tyler', 'Vallejo', 'Vancouver', 'Ventura',
    'Victorville', 'Virginia Beach', 'Visalia', 'Waco', 'Warren', 'Washington',
    'Waterbury', 'West Jordan', 'West Palm Beach', 'West Valley City',
    'Westminster', 'Wichita', 'Wilmington', 'Winston-Salem', 'Worcester',
    'Yonkers')

STREETS = \
    ('10th', '11th', '12th', '13th', '14th', '1st', '2nd', '3rd', '4th', '5th',
     '6th', '7th', '8th', '9th', 'Adams', 'Allen', 'Ash', 'Aspen', 'Birch',
     'Brown', 'Cardinal', 'Cedar', 'Center', 'Cherry', 'Chestnut', 'Church',
     'Clark', 'Cottonwood', 'County Line', 'Cypress', 'Davis', 'Dogwood',
     'Eagle', 'East', 'Eighth', 'Eleventh', 'Elm', 'Evergreen', 'Fairview',
     'Fifth', 'First', 'Forest', 'Fourteenth', 'Fourth', 'Franklin', 'Grant',
     'Green', 'Hickory', 'Highland', 'Hill', 'Hillcrest', 'Hillside',
     'Hilltop', 'Holly', 'Jackson', 'James', 'Jefferson', 'Johnson', 'Jones',
     'Lake', 'Lakeview', 'Laurel', 'Lee', 'Liberty', 'Lincoln', 'Locust',
     'Madison', 'Magnolia', 'Main', 'Maple', 'Martin', 'Meadow', 'Mill',
     'Miller', 'Ninth', 'North', 'Oak', 'Orchard', 'Park', 'Pine', 'Poplar',
     'Railroad', 'Ridge', 'River', 'Rose', 'School', 'Scott', 'Second',
     'Seventh', 'Short', 'Sixth', 'Smith', 'South', 'Spring', 'Spruce',
     'Street Name', 'Street Name', 'Summit', 'Sunrise', 'Sunset', 'Sycamore',
     'Taylor', 'Tenth', 'Third', 'Thirteenth', 'Thomas', 'Twelfth', 'Valley',
     'Village', 'Walnut', 'Washington', 'West', 'Williams', 'Willow', 'Wilson',
     'Woodland')

STATES = \
   ('AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI',
    'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN',
    'MO', 'MS', 'MT', 'NC', 'ND', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK',
    'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA',
    'WI', 'WV', 'WY')


def int_to_b62(num):
    """ Convert integer num to base 62 string. """
    bnum = B62_CHARS[num % 62]
    while num >= 62:
        num //= 62
        bnum = B62_CHARS[num % 62] + bnum
    return bnum


def random_address():
    addr = [str(randint(1, 100))]
    if random() < .05:
        addr.append("%d%s" % (randint(1, 30), choice(('A', 'B', 'C', 'D'))))
    addr.append(choice(STREETS))
    addr.append(choice(('avenue', 'road', 'street')))
    addr.append(choice(CITIES_AND_TOWNS))
    addr.append(choice(STATES))
    addr.append("%05d" % randint(1000, 99999))
    return ' '.join(addr)


def random_b16(n_chars):
    """ Generate random base 16 string 'n_chars' characters long, """
    return ''.join([choice('0123456789abcdef') for _ in range(n_chars)])


def random_b36(n_chars):
    """ Generate random base 62 string 'n_chars' characters long, """
    return ''.join(choices(digits + ascii_uppercase, k=n_chars))


def random_b62(n_chars):
    """ Generate random base 62 string 'n_chars' characters long, """
    return ''.join(choices(B62_CHARS, k=n_chars))


def random_comp(n_chars=10):
    """
    Generate a random composite string 'n_chars' long composed with at least
    one lower case, one upper case, one digit, and one special character.
    Example: nEfZ*rPk2=
    """
    char_types = (digits, ascii_uppercase, ascii_lowercase, '!#$%&*+=?@~^')
    rn = [choice(ch) for ch in char_types]
    for _ in range(n_chars - 4):
        rn.append(choice(choice(char_types)))
    shuffle(rn)
    return ''.join(rn)


def random_date(max_offset_secs=60 * 60 * 24 * 7, latest_date=None):
    """
    Generate a random data relative to 'latest_date' if given, defaults to
    current date/time, and up to 'max_offset_secs' before 'latest_date'.
    """
    if latest_date is None:
        latest_date = to_utc()
    return latest_date - dt.timedelta(seconds=randint(1, max_offset_secs))


def random_digits(n):
    return ''.join([choice(digits) for _ in range(n)])


def random_words(word_ct=2, camel=False, delim=''):
    """
    Generate 'word_ct' random words in camel case if 'camel' True and
    delimited by 'delim'.
    """
    words = [choice(wc) for wc in sample(WORDS, k=word_ct)]
    if camel:
        words = [w.capitalize() if k > 0 else w for k, w in enumerate(words)]
    return delim.join(words)


if __name__ == '__main__':

    import sys

    size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for _ in range(count):
        print(random_comp(size))
