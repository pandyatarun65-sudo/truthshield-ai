"""Demo seed data. All accounts/content are fictional. Demo passwords are for local use only."""

KNOWLEDGE = [
    ("Vaccines cause autism in children", "Large studies covering millions of children found no link between vaccines and autism.", "WHO / CDC", "Health", "FALSE"),
    ("5G mobile towers spread COVID-19", "Viruses cannot travel on radio waves; 5G networks do not spread infectious disease.", "WHO", "Health", "FALSE"),
    ("Drinking hot water or lemon cures viral infections", "No food or drink cures viral infections; use medically approved treatment and vaccines.", "WHO", "Health", "FALSE"),
    ("Injecting or drinking bleach cures infections", "Bleach and disinfectants are toxic and must never be swallowed or injected.", "WHO", "Health", "FALSE"),
    ("The Great Wall of China is visible from space with the naked eye", "It is generally not visible to the naked eye from low Earth orbit.", "NASA", "Science", "MISLEADING"),
    ("Everyone must drink eight glasses of water every day", "Water needs vary by person, climate and activity; there is no single required amount.", "NHS", "Health", "MISLEADING"),
    ("Regular handwashing reduces the spread of infectious diseases", "Handwashing with soap is a proven way to reduce infections.", "WHO", "Health", "TRUE"),
    ("The Earth is flat", "The Earth is an oblate spheroid, confirmed by satellites, ships and flights.", "NASA", "Science", "FALSE"),
    ("Vitamin C prevents the common cold", "Vitamin C does not prevent colds in the general population; it may slightly shorten them.", "Cochrane Review", "Health", "MISLEADING"),
    ("Smoking increases the risk of lung cancer", "Smoking is the leading cause of lung cancer.", "WHO", "Health", "TRUE"),
    ("Climate change is mainly caused by human greenhouse gas emissions", "The scientific consensus is that human emissions are the main driver of recent warming.", "IPCC", "Environment", "TRUE"),
    ("Humans use only ten percent of their brain", "Brain imaging shows we use virtually all of the brain.", "Scientific American", "Science", "FALSE"),
    ("Microwave ovens make food radioactive and cause cancer", "Microwave ovens heat food with non-ionising radiation and do not make it radioactive.", "NHS", "Health", "FALSE"),
    ("Cracking knuckles causes arthritis", "Studies have found no link between knuckle cracking and arthritis.", "Harvard Health", "Health", "FALSE"),
    ("The moon landing was faked in a studio", "Apollo landings are supported by lunar samples, retroreflectors and independent tracking.", "NASA", "Science", "FALSE"),
]

USERS = [  # username, email, password, role
    ("admin", "admin@truthshield.demo", "Admin@12345", "admin"),
    ("moderator", "moderator@truthshield.demo", "Mod@12345", "moderator"),
    ("alice", "alice@truthshield.demo", "User@12345", "user"),
    ("bob", "bob@truthshield.demo", "User@12345", "user"),
    ("carol", "carol@truthshield.demo", "User@12345", "user"),
    ("dave", "dave@truthshield.demo", "User@12345", "user"),
]

POSTS = [  # author, category, text
    ("alice", "Health", "The health ministry reported a slight decrease in seasonal flu cases this week, according to its weekly bulletin."),
    ("alice", "Technology", "The software company released a security update and urged users to install it as soon as possible."),
    ("bob", "Sports", "The national cricket team won the series two to one after a close final match played on Sunday."),
    ("bob", "Health", "Regular handwashing with soap reduces the spread of infectious diseases, as the WHO recommends."),
    ("carol", "Education", "The education board released the examination timetable and said results will be published in June."),
    ("carol", "Science", "The Great Wall of China is visible from space with the naked eye, everybody knows that."),
    ("dave", "Health", "Everyone must drink eight glasses of water every day or their body will fail."),
    ("dave", "Science", "Scientists say the earth is flat and NASA has been hiding it for decades, wake up!"),
    ("alice", "Health", "SHOCKING: Doctors don't want you to know this miracle cure that eliminates cancer in 3 days!!!"),
    ("bob", "Health", "URGENT: 5G towers spread the virus, forward this to 10 people before it's deleted!!!"),
    ("carol", "Health", "My cousin says drinking hot lemon water cures any virus 100% guaranteed, doctors hate this trick"),
    ("dave", "General", "A friend who works at the bank says all ATMs will shut down tomorrow, withdraw everything now!"),
    ("alice", "Environment", "Climate change is mainly caused by human greenhouse gas emissions, according to the IPCC."),
    ("bob", "Politics", "The state government announced a scholarship program for undergraduate students from low income families."),
    ("carol", "Health", "URGENT: SHOCKING!!! Vaccines cause autism in children, a friend who works at the hospital says big pharma is hiding it, forward this before it's deleted!!!"),
    ("dave", "Technology", "Researchers developed a low cost sensor to monitor air quality in crowded cities, the paper reports."),
]
