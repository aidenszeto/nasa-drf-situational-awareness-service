from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class Flyable(Enum, metaclass=MetaEnum):
    pass


class NotFlyable(Enum, metaclass=MetaEnum):
    pass


class Water(Flyable):
    DOCK = "dock"
    RESERVOIR = "reservoir"
    RIVERBANK = "riverbank"
    WATER = "water"
    WETLAND = "wetland"


class Building(Flyable):
    BUILDING = "building"


class School(NotFlyable):
    COLLEGE = "college"
    SCHOOL = "school"
    UNIVERSITY = "university"
    KINDERGARTEN = "kindergarten"


class Government(NotFlyable):
    FIRE_STATION = "fire_station"
    POLICE = "police"
    COURTHOUSE = "courthouse"
    WATER_WORKS = "water_works"
    WASTEWATER_PLANT = "wastewater_plant"
    PRISON = "prison"
    PUBLIC_BUILDING = "public_building"
    LIBRARY = "library"
    POST_OFFICE = "post_office"
    POST_BOX = "post_box"
    COMMUNITY_CENTRE = "community_centre"
    TOWN_HALL = "town_hall"
    MEMORIAL = "memorial"
    MONUMENT = "m"


class Tower(NotFlyable):
    WATER_TOWER = "water_tower"
    COMMS_TOWER = "comms_tower"
    TOWER = "tower"
    OBSERVATION_TOWER = "observation_tower"


class Service(Flyable):
    STATIONERY = "stationery"
    LAUNDRY = "laundry"
    CAR_RENTAL = "car_rental"
    HAIRDRESSER = "hairdresser"
    BANK = "bank"
    CAR_SHARING = "car_sharing"
    TOURIST_INFO = "tourist_info"
    KIOSK = "kiosk"
    TRAVEL_AGENT = "travel_agent"
    TOILET = "toilet"


class Health(NotFlyable):
    VETERINARY = "veterinary"
    HOSPITAL = "hospital"
    OPTICIAN = "optician"
    DENTIST = "dentist"
    DOCTORS = "doctors"
    CLINIC = "clinic"
    PHARMACY = "pharmacy"


class Retail(Flyable):
    CAR_DEALERSHIP = "car_dealership"
    VIDEO_SHOP = "video_shop"
    MALL = "mall"
    FURNITURE_SHOP = "furniture_shop"
    MOBILE_PHONE_SHOP = "mobile_phone_shop"
    GIFT_SHOP = "gift_shop"
    OUTDOOR_SHOP = "outdoor_shop"
    BEAUTY_SHOP = "beauty_shop"
    TOY_SHOP = "toy_shop"
    SPORTS_SHOP = "sports_shop"
    DEPARTMENT_STORE = "department_store"
    SUPERMARKET = "supermarket"
    COMPUTER_SHOP = "computer_shop"
    SHOE_SHOP = "shoe_shop"
    BICYCLE_SHOP = "bicycle_shop"
    CONVENIENCE = "convenience"
    GENERAL = "general"
    MARKET_PLACE = "market_place"
    BOOKSHOP = "bookshop"
    FLORIST = "florist"
    GREENGROCER = "greengrocer"
    CLOTHES = "clothes"
    JEWELLER = "jeweller"


class Entertainment(Flyable):
    NIGHTCLUB = "nightclub"
    THEATRE = "theatre"
    ARTS_CENTRE = "arts_centre"
    ATTRACTION = "attraction"
    CINEMA = "cinema"
    ARTWORK = "artwork"
    SPORTS_CENTRE = "sports_centre"
    PITCH = "pitch"
    MUSEUM = "museum"

class Outdoors(Flyable):
    STADIUM = "stadium"
    GOLF_COURSE = "golf_course"
    ZOO = "zoo"
    PARK = "park"
    DOG_PARK = "dog_park"
    VIEWPOINT = "viewpoint"
    THEME_PARK = "theme_park"
    SWIMMING_POOL = "swimming_pool"
    TRACK = "track"
    ICE_RINK = "ice_rink"
    PLAYGROUND = "playground"
    CAMP_SITE = "camp_site"
    CARAVAN_SITE = "caravan_site"


class Food(Flyable):
    BEVERAGES = "beverages"
    BAKERY = "bakery"
    FAST_FOOD = "fast_food"
    RESTAURANT = "restaurant"
    DRINKING_WATER = "drinking_water"
    BAR = "bar"
    BUTCHER = "butcher"
    FOOD_COURT = "food_court"
    PUB = "pub"
    VENDING_ANY = "vending_any"
    CAFE = "cafe"
    BIERGARTEN = "biergarten"
    WATER_WELL = "water_well"
    PICNIC_SITE = "picnic_site"


class Housing(Flyable):
    MOTEL = "motel"
    HOSTEL = "hostel"
    GUESTHOUSE = "guesthouse"
    HOTEL = "hotel"
    SHELTER = "shelter"
    NURSING_HOME = "nursing_home"
    CHALET = "chalet"


class Misc(Flyable):
    GARDEN_CENTRE = "garden_centre"
    ALPINE_HUT = "alpine_hut"
    RECYCLING_METAL = "recycling_metal"
    ARCHAEOLOGICAL = "archaeological"
    EMBASSY = "embassy"
    RUINS = "ruins"
    CAR_WASH = "car_wash"
    LIGHTHOUSE = "lighthouse"
    CHEMIST = "chemist"
    CASTLE = "castle"
    DOITYOURSELF = "doityourself"
    WATER_MILL = "water_mill"
    RECYCLING = "recycling"
    FOUNTAIN = "fountain"
    WAYSIDE_SHRINE = "wayside_shrine"
    GRAVEYARD = "graveyard"
    MONUMENT = "monument"