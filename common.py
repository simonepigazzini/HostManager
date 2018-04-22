#!/bin/python3

from collections import OrderedDict as odict

buildings = ["Villa Maria", "Palazzo Iargia", "Siracusa"]

rooms_bld_map = {"Villa Maria": ["Double", "Triple", "All"], "Palazzo Iargia" : ["Rosa", "Blu", "Bianca"], "Siracusa" : ["Monolocale", "Bilocale"]}

agents = ["None", "Mariagrazia", "Salvo"]

agencies = ["None", "Booking-Online", "Booking-Hotel", "Airbnb", "Homeaway", "Expedia-Expedia Collect", "Expedia-Hotel Collect"]

internet_opt = ["Not included", "Included"]

customer_default = odict([
        ("id" , -1),
        ("fullname" ,  "Enter customer full name"),
        ("nguests" ,  "Enter number of guests"),
        ("phone" ,  "+XX-##########"),
        ("building" , buildings),
        ("room" ,  rooms_bld_map["Villa Maria"]),
        ("arrival" ,  "dd/mm/year"),
        ("departure" ,  "dd/mm/year"),
        ("nights" ,  ""),
        ("agency" , agencies),
        ("agency_fee" ,  "fee (euro),"),
        ("agent" , agents),
        ("cleanings" , "Mariagrazia"),
        ("internet", internet_opt),
        ("notes", "Notes on customer"),
        ("night_fare" , "price"),
        ("extras" ,  "extras total price"),
        ("total_price" ,  "total"),
        ("payed" , "0"),
        ("balance" , "")
])
