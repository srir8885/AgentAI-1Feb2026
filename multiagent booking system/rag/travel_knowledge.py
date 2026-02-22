"""
Static travel knowledge base seeded into Pinecone.

Each Document has a `page_content` (the text chunk that gets embedded) and
`metadata` (used for optional filtered searches).
"""

from langchain_core.documents import Document

TRAVEL_DOCUMENTS: list[Document] = [

    # ── Destinations ───────────────────────────────────────────────────

    Document(
        page_content="""London, United Kingdom – Complete Travel Guide

Top Attractions: Big Ben and the Houses of Parliament, Tower of London, \
Buckingham Palace, The British Museum, The National Gallery, Hyde Park, \
Tower Bridge, St. Paul's Cathedral, Borough Market, Covent Garden.

Best Time to Visit: May–September for pleasant weather (18–24 °C). \
December for Christmas markets. July–August is peak season.

Local Transportation: Oyster Card for the Underground (Tube), buses, and \
overground trains. Tube runs 05:00–midnight (24 h on weekends on some lines). \
Heathrow Express connects the airport to central London in 15 minutes.

Currency: British Pound (GBP). Contactless card payments accepted everywhere.

Cultural Tips: Queuing is taken very seriously — always form orderly lines. \
Tip 10–15 % in restaurants. Pub culture is central to London life.

Cuisine: Full English breakfast, fish and chips, afternoon tea, diverse \
international food scene. Borough Market is excellent for food lovers.

Safety: Generally safe; watch for pickpockets in tourist areas. Emergency: 999.

Visa: Most nationalities can visit for up to 6 months without a visa. \
Check the UKVI website for your specific nationality.""",
        metadata={"destination": "london", "type": "destination_guide", "region": "europe"},
    ),

    Document(
        page_content="""Paris, France – Complete Travel Guide

Top Attractions: Eiffel Tower, The Louvre, Notre-Dame Cathedral, \
Arc de Triomphe, Champs-Élysées, Montmartre and Sacré-Cœur, Palace of \
Versailles (day trip), Musée d'Orsay, Seine River Cruise, Centre Pompidou.

Best Time to Visit: April–June (spring) for mild weather and blooming gardens. \
September–October (fall) for fewer crowds. December for Christmas magic. \
Avoid August — many Parisians leave and some shops close.

Local Transportation: Metro (16 lines) is extensive and efficient. Buy a \
carnet (10 tickets) for savings. Vélib' bike-sharing is popular. \
RER trains connect to CDG and Orly airports.

Currency: Euro (EUR). Credit cards widely accepted; ATMs abundant.

Cultural Tips: Always greet with "Bonjour" — it goes a long way. Dining \
takes 2+ hours — it's a social experience. Dress smartly; Parisians are \
fashion-conscious. Avoid eating while walking.

Cuisine: Croissants, baguettes, crêpes, French onion soup, steak frites, \
macarons, crème brûlée. Café culture is central. Many excellent bistros \
and Michelin-starred restaurants.

Safety: Generally safe; watch for pickpockets on the Metro and near the Eiffel \
Tower. Emergency: 112.""",
        metadata={"destination": "paris", "type": "destination_guide", "region": "europe"},
    ),

    Document(
        page_content="""Tokyo, Japan – Complete Travel Guide

Top Attractions: Senso-ji Temple (Asakusa), Shibuya Crossing, Tokyo Skytree, \
Harajuku / Takeshita Street, Shinjuku Gyoen Garden, teamLab digital art \
museums, Akihabara (electronics/anime), Tsukiji outer market, Meiji Shrine, \
DisneySea / Tokyo Disneyland.

Best Time to Visit: March–April for cherry blossoms (sakura). \
October–November for autumn foliage. May and September–October for pleasant \
temperatures and fewer crowds. Avoid July–August (heat and humidity) and \
Golden Week (late April–early May, massive crowds).

Local Transportation: IC Card (Suica or Pasmo) for trains, subways, and \
buses. JR Pass for bullet trains (Shinkansen) across Japan. \
Tokyo Metro Day Pass for unlimited daily subway rides. Taxis are expensive.

Currency: Japanese Yen (JPY). Japan is still largely cash-based — always \
carry yen. ATMs at 7-Eleven and Japan Post accept foreign cards.

Cultural Tips: Remove shoes when entering homes or traditional restaurants. \
Don't eat or drink while walking. Queue orderly and speak quietly on public \
transport. Tipping is NOT practiced — it can be considered rude. Bow as a \
greeting.

Cuisine: Sushi, ramen, tempura, wagyu beef, izakaya (pub dining), conveyor-belt \
sushi, yakitori, tonkatsu, miso soup. Incredible variety at all price points.

Safety: One of the safest cities in the world. Emergency: 110 (police) / 119 \
(ambulance/fire).

Visa: Many nationalities receive 90-day visa-free entry.""",
        metadata={"destination": "tokyo", "type": "destination_guide", "region": "asia"},
    ),

    Document(
        page_content="""Dubai, UAE – Complete Travel Guide

Top Attractions: Burj Khalifa (world's tallest building), Dubai Mall and \
Dubai Fountain, Palm Jumeirah, Dubai Creek / Gold Souk, Deira Spice Market, \
Dubai Frame, Desert Safari with dune bashing, Jumeirah Beach, Dubai Marina, \
Global Village (seasonal).

Best Time to Visit: November–April (20–30 °C). Avoid May–September (temps \
exceed 40 °C). Respect Ramadan customs — no eating or drinking in public \
during daylight.

Local Transportation: Dubai Metro (Red and Green lines). Metered taxis, \
Careem/Uber, RTA buses, and water taxis (Abra) in the old Creek.

Currency: UAE Dirham (AED), pegged to USD. Major cards widely accepted.

Cultural Tips: Dress modestly in public (cover shoulders and knees). \
No public displays of affection. Alcohol only in licensed venues (hotels, bars). \
No photography of locals without permission. Friday is the holy day.

Cuisine: Shawarma, hummus, falafel, grilled meats, fresh seafood. \
Every global cuisine is represented in luxury hotels. Traditional Emirati \
food worth seeking out.

Shopping: Dubai Duty Free, Dubai Mall, Mall of the Emirates, Gold Souk, \
Spice Souk. Dubai Shopping Festival (Jan–Feb) and Dubai Summer Surprises.

Safety: Very safe city with strict laws. Emergency: 999.""",
        metadata={"destination": "dubai", "type": "destination_guide", "region": "middle_east"},
    ),

    Document(
        page_content="""Bali, Indonesia – Complete Travel Guide

Top Attractions: Tanah Lot Sea Temple, Ubud Monkey Forest, Tegallalang Rice \
Terraces, Kuta and Seminyak Beaches, Mount Batur sunrise trek, Uluwatu Temple \
with Kecak dance, Tirta Empul water temple, Ubud art galleries and markets.

Best Time to Visit: April–October (dry season), especially May–June and \
September–October to avoid peak crowds. July–August is high season with higher \
prices. November–March is wet season with heavy afternoon rains.

Local Transportation: Motorbike rental (~$5/day). Private driver/guide for \
day trips (~$40–60/day). Gojek/Grab apps for affordable rides. \
No reliable public bus network.

Currency: Indonesian Rupiah (IDR). ATMs widely available. Cash preferred at \
local warungs and markets — negotiate prices at markets.

Cultural Tips: Bali is predominantly Hindu — wear a sarong at temples. \
Don't touch people's heads (sacred). Point with your thumb, not index finger. \
Step over (not on) offerings placed on the ground.

Cuisine: Nasi goreng (fried rice), mie goreng (fried noodles), satay, \
babi guling (suckling pig), bebek betutu (slow-cooked duck), fresh Jimbaran \
seafood. Ubud has excellent vegan/vegetarian options.

Health: Drink only bottled water. Use mosquito repellent. \
Travel insurance is essential.

Visa: Visa on arrival for 40+ nationalities (30 days, extendable). \
E-Visa available for others.""",
        metadata={"destination": "bali", "type": "destination_guide", "region": "asia"},
    ),

    Document(
        page_content="""New York City, USA – Complete Travel Guide

Top Attractions: Statue of Liberty, Central Park, Times Square, \
Metropolitan Museum of Art (The Met), Brooklyn Bridge, Empire State Building, \
The High Line, 9/11 Memorial, MoMA, One World Trade Center, Broadway shows.

Best Time to Visit: April–June (spring) and September–November (fall) for \
ideal weather. December for Christmas atmosphere and ice skating. \
July–August is hot and humid but packed with free events.

Local Transportation: NYC Subway (24/7) — buy a MetroCard or use OMNY \
tap-to-pay. Extensive bus network. Yellow cabs and Uber/Lyft everywhere. \
Walking is the best way to explore Manhattan below 59th Street.

Currency: US Dollar (USD). Cards accepted everywhere. \
Tip 18–22 % at restaurants — this is expected.

Cultural Tips: New Yorkers walk fast — don't stop abruptly on sidewalks. \
Stand right, walk left on escalators. The city never sleeps — \
most things are available 24/7.

Cuisine: New York–style pizza (thin crust, sold by the slice), \
bagels with lox, hot dogs from street carts, pastrami sandwiches, \
dim sum in Chinatown, world-class fine dining.

Neighborhoods: Manhattan (Times Square, Wall St, Harlem), Brooklyn \
(Williamsburg, DUMBO), Queens (Flushing — great Asian food), Bronx \
(Yankee Stadium, Little Italy).

Safety: Safe in tourist areas; avoid flashing valuables. Emergency: 911.""",
        metadata={"destination": "new york", "type": "destination_guide", "region": "north_america"},
    ),

    Document(
        page_content="""India – Comprehensive Travel Guide

Popular Destinations:
• Delhi: Red Fort, Qutub Minar, India Gate, Chandni Chowk old bazaar.
• Agra: Taj Mahal (UNESCO), Agra Fort, Fatehpur Sikri.
• Jaipur: Amber Fort, Hawa Mahal, City Palace, Pink City markets.
• Mumbai: Gateway of India, Marine Drive, Dharavi, Bollywood studios.
• Goa: Baga and Anjuna beaches, Old Goa churches, vibrant nightlife.
• Kerala: Backwaters houseboat, Munnar tea gardens, Varkala beach.
• Rajasthan: Jaisalmer desert safaris, Udaipur lakes, Jodhpur Blue City.
• Varanasi: Ganges ghats, spiritual rituals and ceremonies.

Best Time to Visit: October–March (cool dry weather). \
Avoid June–September (monsoon) for most regions.

Visa: e-Visa available for 160+ nationalities (indianvisaonline.gov.in). \
Apply 4+ days ahead. 30-day, 1-year, and 5-year options.

Transportation: Indian Railways (book on IRCTC early). \
Domestic flights via IndiGo and Air India. Ola/Uber in cities. \
Auto-rickshaws negotiate or use Ola.

Health: Drink only bottled/filtered water. Eat freshly cooked, hot food. \
Vaccinations: Hepatitis A and Typhoid essential. \
Carry ORS and Imodium for traveller's diarrhoea.

Currency: Indian Rupee (INR). Cash important for smaller establishments.""",
        metadata={"destination": "india", "type": "destination_guide", "region": "asia"},
    ),

    Document(
        page_content="""Rome, Italy – Travel Guide

Top Attractions: Colosseum (book tickets online — essential to skip lines), \
Roman Forum, Vatican City (St. Peter's Basilica, Sistine Chapel), \
Pantheon, Trevi Fountain, Spanish Steps, Borghese Gallery, Trastevere district.

Day Trips: Pompeii and Herculaneum (2 h by train), Amalfi Coast, Ostia Antica.

Best Time to Visit: April–May and September–October for pleasant temperatures \
and manageable crowds. June–August is hot (30–38 °C) and very busy. \
December–January is quieter and cheaper.

Transportation: Rome Metro (2 main lines). Buses for broader coverage. \
Walking is the best way to explore the historic centre. \
Taxis use meters — always request a meter.

Cuisine: Carbonara, cacio e pepe, supplì (fried rice balls), \
Roman artichokes (carciofi alla romana), gelato, espresso. \
Eat where locals eat — avoid tourist-trap restaurants near major sites.

Cultural Tips: Dress modestly to enter churches (cover shoulders and knees). \
Drinking from Rome's free street fountains (nasoni) is safe and refreshing. \
Tipping not obligatory but rounding up is appreciated.

Visa: Schengen Visa. EU/EEA citizens need passport. \
Many other nationalities are visa-free for 90 days.""",
        metadata={"destination": "rome", "type": "destination_guide", "region": "europe"},
    ),

    Document(
        page_content="""Barcelona, Spain – Travel Guide

Top Attractions: Sagrada Família (Gaudí masterpiece — book months ahead!), \
Park Güell, Casa Batlló, La Barceloneta Beach, La Rambla (watch pickpockets!), \
Picasso Museum, Gothic Quarter (Barri Gòtic), Camp Nou stadium.

Best Time to Visit: May–June and September–October (pleasant, less crowded). \
July–August is hot (30 °C+) and very busy with higher prices.

Local Transportation: Metro, bus, and tram. T-Casual 10-trip card for savings. \
Cycling is popular — Bicing bike-share. Walking in the Gothic Quarter.

Cuisine: Tapas, patatas bravas, jamón ibérico, paella, fideuà, pan con tomate, \
cava. La Boqueria market for fresh produce (go early — very touristy).

Cultural Tips: Catalan identity is strong — learn a few words of Catalan \
alongside Spanish. Lunch is the main meal (2–4 pm); many restaurants close \
between 4–8 pm. Nightlife starts very late (midnight onward).

Visa: Schengen Zone. EU/EEA citizens enter freely.""",
        metadata={"destination": "barcelona", "type": "destination_guide", "region": "europe"},
    ),

    Document(
        page_content="""Bangkok, Thailand – Travel Guide

Top Attractions: Grand Palace and Wat Phra Kaew, Wat Arun (Temple of Dawn), \
Wat Pho (reclining Buddha), Chatuchak Weekend Market, \
Khao San Road (backpacker hub), Lumphini Park, Damnoen Saduak Floating Market, \
Asiatique night market, rooftop bars.

Best Time to Visit: November–February (cool and dry, ~28 °C). \
March–May is hot (35–40 °C). June–October is rainy season — \
frequent afternoon downpours but cheap accommodation.

Local Transportation: BTS Skytrain and MRT Metro. Express boats on the \
Chao Phraya River. Tuk-tuks (negotiate first). Grab app for cheap rides. \
Songthaews (shared minibuses) in outer areas.

Currency: Thai Baht (THB). ATMs widely available (fee per withdrawal). \
Cash preferred at markets and street stalls.

Cultural Tips: Show respect at temples (dress modestly, remove shoes). \
Never disrespect the Royal Family — it is illegal. \
The "wai" (hands pressed together, slight bow) is the standard greeting. \
Bargaining is expected at markets.

Cuisine: Pad Thai, tom yum soup, green/red/massaman curries, mango sticky rice, \
som tum (papaya salad), street food on every corner. Incredible value.

Visa: Visa exemption for 60+ nationalities for 30 days (extended to 60 days).""",
        metadata={"destination": "bangkok", "type": "destination_guide", "region": "asia"},
    ),

    # ── Travel Tips ──────────────────────────────────────────────────────

    Document(
        page_content="""Essential International Travel Tips

Passport and Documentation:
• Passport validity: Most countries require 6 months validity beyond your stay.
• Photocopy passport, visa, and travel insurance — store separately from originals.
• Keep digital copies in email or cloud storage (Google Drive, iCloud).
• Check visa requirements at least 2–3 months before travel.

Money and Finances:
• Notify your bank of international travel plans to avoid card blocks.
• Carry some local currency for arrival — airport exchange rates are poor.
• Mix of credit + debit cards is safer than relying on one.
• Keep $100–200 USD as emergency backup.
• Use ATMs inside banks or shopping malls; avoid standalone machines.

Health and Safety:
• Purchase comprehensive travel insurance before any trip.
• Check CDC.gov for vaccination recommendations by destination.
• Pack prescription medications in carry-on with original pharmacy labels.
• Research local emergency numbers and nearest hospitals.
• Get travel vaccinations 4–6 weeks before departure.

Packing Tips:
• Pack in layers — weather is unpredictable.
• Roll clothes instead of folding to save space.
• Always carry essentials (medications, a change of clothes) in your carry-on.
• Download offline maps (Google Maps offline) before travel.

Staying Connected:
• Buy a local SIM or international eSIM (Airalo app is popular).
• Download WhatsApp for international messaging.
• Offline translation apps — download Google Translate language packs.
• Use a VPN on public WiFi for security.""",
        metadata={"type": "travel_tips", "category": "general"},
    ),

    Document(
        page_content="""Budget Travel Guide – Saving Money While Travelling

Flights:
• Book 6–8 weeks ahead for domestic, 3–6 months for international.
• Use Google Flights, Skyscanner, or Kayak for comparison.
• Set price alerts on Google Flights.
• Tuesday/Wednesday flights are often the cheapest.
• Budget airlines: Ryanair and easyJet in Europe; AirAsia and IndiGo in Asia.
• Be flexible with dates to find the best prices.
• Connecting flights can be significantly cheaper than direct.

Accommodation:
• Hostels: $10–30/night — great for solo travellers.
• Airbnb: Better value for groups and longer stays.
• Booking.com and Hotels.com for deals with free cancellation.
• Booking directly with hotels can sometimes yield better rates.

Food:
• Eat where locals eat — street food and local restaurants.
• Cook in hostel kitchens for longer stays.
• Lunch specials are often better value than dinner.
• Supermarkets for breakfast and snacks.

Activities:
• Many museums offer free days or reduced-entry times.
• City tourism cards often include transport + top attractions.
• Free walking tours (tip-based) operate in most cities.
• National parks, beaches, and hiking trails are free or very low cost.

General Budget Tips:
• Travel in shoulder season (spring/fall) for lower prices.
• Asia and Eastern Europe offer excellent value.
• Slower travel = lower costs (fewer transport changes).""",
        metadata={"type": "travel_tips", "category": "budget"},
    ),

    Document(
        page_content="""Airport and Flight Travel Tips

Before Your Flight:
• Check in online 24–48 hours before departure to choose seats.
• Arrive 2–3 hours early for international flights, 90 min for domestic.
• Check baggage allowance and weigh bags at home to avoid fees.
• Liquids: max 100 ml per container, in a clear plastic bag for security.
• Keep passport and boarding pass easily accessible.

Carry-On Essentials:
• Passport, visa, travel insurance documents.
• Phone charger and portable power bank.
• Neck pillow and eye mask for long-haul flights.
• Noise-cancelling headphones.
• Change of clothes in case luggage is delayed.
• Prescription medications.
• Empty water bottle to fill after security.

Long-Haul Comfort:
• Dress in layers (planes can be cold).
• Stay hydrated — drink water; limit alcohol and caffeine.
• Walk every 1–2 hours to prevent DVT.
• Compression socks for flights over 4 hours.
• Adjust mentally to destination time zone.

Connecting Flights:
• Allow minimum 2 hours for international connections (3 h in busy airports).
• Check whether you need a transit visa.
• If on the same ticket, the airline is responsible for missed connections.

Flight Hacks:
• Use Google Flights 'Explore' for cheap destination inspiration.
• Browse in incognito mode — cookie tracking can inflate prices.
• Consider positioning flights to major hubs for better deals.""",
        metadata={"type": "travel_tips", "category": "flights_airports"},
    ),

    # ── Visa and Health ───────────────────────────────────────────────────

    Document(
        page_content="""Visa and Entry Requirements Guide

Types of Visas:
• Tourist/Visitor Visa: Leisure travel, usually 30–90 days.
• Transit Visa: Passing through a country en route to another destination.
• Business Visa: Meetings and conferences (not employment).
• e-Visa: Applied online before travel; printed or digital.
• Visa on Arrival (VoA): Obtained at the airport/border upon arrival.

Common Entry Requirements:
• Valid passport (6+ months of validity is standard).
• Completed visa application form.
• Passport-sized photographs.
• Proof of accommodation (hotel booking).
• Return or onward flight ticket.
• Proof of sufficient funds.
• Travel insurance.
• Bank statements (last 3–6 months).

Visa-Free Access (Major Destinations):
• Schengen Area (26 European countries): visa-free for 60+ nationalities, up to 90 days.
• USA: ESTA for visa-waiver countries; B-1/B-2 visa for others.
• UK: Visa-free for many nationalities, up to 6 months.
• Japan: Visa-free for 68+ nationalities, up to 90 days.
• Australia: eVisitor or ETA for eligible nationalities.

Application Tips:
• Apply 2–3 months in advance for visa appointments.
• US and UK visas can have very long appointment wait times.
• Always check official embassy websites for current information.
• Keep copies of all submitted documents.""",
        metadata={"type": "requirements", "category": "visa"},
    ),

    Document(
        page_content="""Travel Health and Vaccination Guide

Recommended Vaccinations by Region:

Southeast Asia (Thailand, Vietnam, Indonesia, Philippines):
• Hepatitis A and B
• Typhoid
• Japanese Encephalitis (rural areas, extended stays)
• Rabies (if working with animals)
• Malaria prophylaxis for some rural areas

Africa (Sub-Saharan):
• Yellow Fever (required for entry to some countries)
• Malaria prophylaxis (essential for most regions)
• Hepatitis A and B, Typhoid
• Meningococcal meningitis, Rabies

South America:
• Yellow Fever (Amazon regions)
• Hepatitis A and B, Typhoid
• Malaria (Amazon basin)

Standard Vaccinations for All International Travel:
• COVID-19 (check current entry requirements)
• Routine vaccinations up to date (MMR, tetanus, flu)

Travel Health Tips:
• Visit a travel clinic 4–6 weeks before departure.
• Check CDC (cdc.gov/travel) for destination-specific advice.
• Bring prescription medications in original containers.
• Carry a basic first-aid kit.
• Food safety in high-risk areas: "Boil it, cook it, peel it, or forget it."

Travel Insurance – Health Coverage:
• Emergency medical evacuation (can cost $50,000–$100,000+).
• Hospital stays abroad, emergency dental.
• Trip cancellation for medical reasons.
• 24/7 emergency assistance hotline.""",
        metadata={"type": "requirements", "category": "health"},
    ),

    # ── Europe Regional ───────────────────────────────────────────────────

    Document(
        page_content="""European Travel Guide – Schengen Zone and Top Destinations

Schengen Zone:
• 26 countries with no internal border controls.
• 90 days in any 180-day period for most non-EU visitors.
• A single Schengen Visa is valid for all member states.
• Members include: France, Germany, Italy, Spain, Netherlands, Greece, \
  Portugal, Austria, Switzerland, and more.
• UK, Ireland, Bulgaria, and Romania are NOT in Schengen.

Getting Around Europe:
• Eurail Pass for extensive rail travel across multiple countries.
• Budget airlines: Ryanair, easyJet for inter-city hops.
• Flixbus for budget coach travel.
• Car rental ideal for rural areas and flexible itineraries.

Best Seasons:
• Spring (April–May): Shoulder season — good weather, fewer tourists.
• Summer (June–August): Peak season — crowded and pricey.
• Fall (September–October): Excellent — local feel returns.
• Winter: Christmas markets in Germany, Austria, and Czech Republic are magical.

Amsterdam, Netherlands:
• Anne Frank House (advance booking essential), Van Gogh Museum, Rijksmuseum.
• Canal boat tours, day trips to Zaanse Schans and Keukenhof (tulips in spring).
• Cycling culture — rent a bike to explore like a local.

Prague, Czech Republic:
• Prague Castle, Charles Bridge, Old Town Square.
• One of Europe's best value capitals.
• Excellent local beer culture.""",
        metadata={"type": "destination_guide", "region": "europe", "category": "regional_guide"},
    ),
]
