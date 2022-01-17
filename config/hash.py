# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

"""
    These are the attributes possible to select for each run.
    This way it is very simple to add new attributes.
    Each of them gets "sluggyfied“ and used in the API.
    i.e.: a 'Men-only Hash‘ will be formatted to ‘men-only-hash’ using
    this function 'common/misc.py#L16-L51'

    The consuming side needs be made aware of
    ony changes happening here.
"""
hash_attributes = [
    'Accessible by public transport',
    'Bag drop available',
    'No bag drop available',
    'Kids allowed',
    'Bring flashlight',
    'Water on trail',
    'Walker trail',
    'Runner trail',
    'Long run trail',
    'On after',
    'Baby jogger friendly',
    'City run',
    'Live hare',
    'Dead hare',
    'Nighttime run',
    'Harriette run',
    'Men-only Hash',
    'Woman-only Hash',
    'No kids allowed',
    'Pub crawl',
    'Shiggy run',
    'Bike Hash',
    'Steep hills',
    'Charity event',
    'Dog friendly',
    'Pick-up Hash',
    'Catch the Hare',
    'Bring cash on trail',
    'AGM'
]

"""
    The same principals of formatting apply to 'hash_scope' as to
    'hash_attributes'. The consuming side needs be made aware of
    ony changes happening here.
"""
hash_scope = [
    "Unspecified",
    "Do not promote",
    "Promote locally",
    "Promote regionally", 
    "Promote nationally",
    "Promote continent wide",
    "Promote worldwide",
    "Other special event"
]

# EOF
