from scrapers import SunScraper, CleaningScraper, SkinScraper

GUIDES_SUBCATEGORIES_URL = 'https://www.ewg.org/guides/subcategories/'

SUNSCREEN_URL = 'https://www.ewg.org/sunscreen/about-the-sunscreens/'

BROWSE_CATEGORY_URL = 'https://www.ewg.org/skindeep/browse/category/'

SKIN_DEEP = {
    'Personal Care': {
        'Sun': {
            'scraper': SunScraper,
            'base_url': SUNSCREEN_URL,
            'child': {
                'Daily use SPF': '?category=moisturizer+with+SPF',
                'Recreational sunscreen': '?category=beach+%26+sport+sunscreen'
            }
        },
        'Skin': {
            'scraper': SkinScraper,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Bar Soap': 'Bar_soap',
                'Bath Oil/Salts/Soak': 'Bath_oil__salts__soak',
                'Body Wash': 'Body_wash__cleanser',
                'Facial Cleanser': 'Facial_cleanser',
                'Hand Sanitizer': 'Hand_sanitizer',
                'Liquid Hand Soap': 'Liquid_hand_soap',
                'Moisturizer': 'Moisturizer',
                'Deodorant': 'Antiperspirant__deodorant'
            }
        },
        'Hair': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Shampoo': 'Shampoo',
                'Conditioner': 'Conditioner',
                'Hair Spray': 'Hair_spray',
                'Shaving Cream': 'Shaving_cream?marketed_for=kinky_hair',
                'Styling Gel': 'Styling_gel__lotion?marketed_for=kinky_hair'
            }
        },
        'Oral Care': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Toothpaste': 'Toothpaste',
                'Tooth Whitening': 'Tooth_whitening',
                'Mouthwash': 'Mouthwash'
            }
        },
        'Men': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Body Spray': 'Body_spray/?marketed_for=men',
                'Body Wash': 'Body_wash__cleanser/?marketed_for=men',
                'Beard Oil': 'Beard_oil',
                'Facial Cleanser': 'Facial_cleanser/?marketed_for=men',
                'Beard Cleanser': 'Beard_cleanser',
                'Deodorant': 'Antiperspirant__deodorant/?marketed_for=men'
            }
        }
    },
    'Makeup': {
        'Face': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Concealer': 'Concealer',
                'Foundation': 'Foundation',
                'Bronzer': 'Bronzer__Highlighter'
            }
        },
        'Eyes': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Eyeshadow': 'Eye_shadow'
            }
        },
        'Lips': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Lipstick': 'Lipstick'
            }
        },
        'Fragrance': {
            'scraper': None,
            'base_url': BROWSE_CATEGORY_URL,
            'child': {
                'Body Spray': 'Body_Spray',
                'Fragrance for Men': 'Fragrance_for_men',
                'Fragrance for Women': 'Fragrance_for_women'
            }
        }
    }
}


CLEANING = {
    'Household': {
        'All Purpose': {
            'scraper': CleaningScraper,
            'base_url': GUIDES_SUBCATEGORIES_URL,
            'child': {
                'General Purpose Cleaner': '3-GeneralPurposeCleaner',
                'Disinfectant': '67-Disinfectant',
                'Glass/Window Cleaner': '4-GlassWindowCleaner'
            }
        },
        'Bathroom': {
            'scraper': CleaningScraper,
            'base_url': GUIDES_SUBCATEGORIES_URL,
            'child': {
                'Toilet Cleaner': '11-ToiletCleaner',
                'Tub/Tile/Sink Cleaner': '9-TubTileSinkCleaner'
            }
        },
        'Dishwashing': {
            'scraper': CleaningScraper,
            'base_url': GUIDES_SUBCATEGORIES_URL,
            'child': {
                'Dishwasher Detergent': '24-DishwasherDetergent',
                'Dishwashing Pods & Pouches': '199-DishwashingPodsPouches',
                'Hand Washing Detergent': '25-HandWashingDetergent'
            }
        },
        'Kitchen': {
            'scraper': CleaningScraper,
            'base_url': GUIDES_SUBCATEGORIES_URL,
            'child': {
                'General Purpose Cleaner': '38-GeneralPurposeCleanerKitchen',
                'Stove Top Cleaner': '44-StoveTopCleaner',
                'Granite/Stone Cleaner': '40-GraniteStoneCleaner'
            }
        },
        'Laundry': {
            'scraper': CleaningScraper,
            'base_url': GUIDES_SUBCATEGORIES_URL,
            'child': {
                'Laundry Detergent, General Purpose': '47-LaundryDetergentGeneralPurpose',
                'Laundry Detergent, HE': '49-LaundryDetergentHE',
                'Laundry Pods & Pouches': '198-LaundryPodsPouches'
            }
        }
    }
}


EWG_DATABASES = {
    'skin': SKIN_DEEP,
    'cleaning': CLEANING
}