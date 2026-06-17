from decimal import Decimal
from listings.models import Listing

def global_platform_settings(request):
    """
    Dynamically feeds active product tickers, UI translations, and legally 
    compliant Zimbabwean Terms & Conditions/FAQs into the application framework.
    """
    usd_to_zig_mid_rate = Decimal('26.50')
    
    # Fetch live product prices from database table
    active_listings = Listing.objects.filter(is_active=True, is_paid=True).only('title', 'price')[:10]
    marquee_items = []
    for item in active_listings:
        zig_price = item.price * usd_to_zig_mid_rate
        marquee_items.append(f"{item.title}: ${item.price:.2f} USD / ZiG {zig_price:.2f}")
    
    current_lang = request.COOKIES.get('django_language') or request.session.get('django_language', 'en')

    # 📋 Dynamic Compliance & FAQ Content Engine (Completely Variable-Driven)
    faq_and_terms_matrix = {
        'en': {
            'faq_title': "Frequently Asked Questions (FAQs)",
            'faq_q1': "Q: Who can legally list assets on this platform?",
            'faq_a1': "A: Only verified primary legal owners, direct equipment manufacturers, or officially deeded titleholders. Speculative brokers, agents, or unverified middlemen are strictly banned under local market anti-hoarding policies.",
            'faq_q2': "Q: How are transaction pricing and asset rates calculated?",
            'faq_a2': "A: All pricing metrics are fixed directly by the asset owner. Conversions display dynamically using national mid-rate indicators to remain compliant with Zimbabwean multi-currency pricing legal guidelines.",
            
            'terms_title': "Legally Articulated Terms of Service",
            'terms_p1': "1. Consumer Protection Framework: Pursuant to the Consumer Protection Act [Chapter 14:44], users warrant that all technical descriptions, specifications, ownership documents, and imagery uploaded represent true asset status. False advertising or malicious price-gouging triggers immediate account termination.",
            'terms_p2': "2. Cybersecurity & Data Shield: In alignment with the Cyber Security and Data Protection Act [Chapter 12:07], personal user cell lines, digital tokens, and verification parameters are encrypted securely. They will never be sold, scraped, or shared with third-party advertising companies.",
            'terms_p3': "3. Anti-Agent Mandate: This platform maintains a strict zero-tolerance enforcement loop against ghost-brokers and duplicate listing rings. Attempting to claim title over an asset belonging to another individual will result in an immediate permanent ban and submission of details to local fraud units."
        },
        'sn': {
            'faq_title': "Mibvunzo Inowanzo Bvunzwa (FAQ)",
            'faq_q1': "M: Ndianani anotenderwa kuisa midziyo pano?",
            'faq_a1': "M: Varidzi vechokwadi vemitemo chete kana vanogadzira midziyo zviri pamutemo. Ma broker nemavanyengeri akadziviswa zvachose pasi pemitemo yedu.",
            'faq_q2': "M: Mitengo inofambiswa sei pakati pe USD ne ZiG?",
            'faq_a2': "M: Mitengo inoiswa nemuridzi wemidziyo pachake. Isu tinotendeutsa mitengo tichishandisa mwero webhangi guru re Zimbabwe kutevedzera mutemo.",
            
            'terms_title': "Mitemo neZvirongwa Zvemushandisi",
            'terms_p1': "1. Kuchengetedza Mutengi: Pasi pemutemo we Consumer Protection Act [Chapter 14:44], unotsinhira kuti mifananidzo nerondedzero yaunopinza ndeyechokwadi. Kunyepa kunounza kuvharwa kweakhaundi ipapo ipapo.",
            'terms_p2': "2. Kuchengetedza Mashoko Muvande: Kutevedzera mutemo we Cyber Security and Data Protection Act [Chapter 12:07], nhamba dzenhare dzenyu nemagwaro zvinochengetedzwa zvakavharirwa zvakanyanya.",
            'terms_p3': "3. Kurambidza MaBroker: Hatitenderi munhu anopinza chigadzirwa chisiri chake kana kuisa mifananidzo yakadzokororwa yeimwe akhaundi."
        },
        'nd': {
            'faq_title': "Imibuzo Ejwayelekileyo Ukubvunzwa (FAQ)",
            'faq_q1': "B: Ngubani ovunyelweyo ukufaka impahla lapha?",
            'faq_a1': "B: Abanikazi bempahla beqiniso kuphela labo abavunyelwe ngomthetho. Omancitshana lababambeli bavalelwe kude.",
            'faq_q2': "B: Inkokhelo ibalwa njani phakathi kwe USD le ZiG?",
            'faq_a2': "B: Intengo ibekwa ngumnikazi wempahla. Isistimu iguqula inkokhelo isebenzisa umthetho webhanga elikhulu le Zimbabwe.",
            
            'terms_title': "Imithetho Lesimo Sokusetshenziswa",
            'terms_p1': "1. Ukuvikelwa Komthengi: Kuye ngomthetho we Consumer Protection Act [Chapter 14:44], uqinisekisa ukuthi yonke imininingwane oyifakayo iqondile. Amanga aletha ukubvalwa kwe-akhawunti.",
            'terms_p2': "2. Ukuvikelwa Kwemininingwane: Ngokuvumelana lomthetho we Cyber Security and Data Protection Act [Chapter 12:07], inombolo zakho zocingo zivikelekile kakhulu.",
            'terms_p3': "3. Ukwenqatshelwa Komancitshana: Asibavumeli abantu abafaka izithombe ezifanayo kumi-akhawunti ehlukahlukene."
        }
    }

    # 🌐 Base Layout Translation Dictionary
    translations_pool = {
        'en': {
            'live_feed': "Live Product Feed", 'settings': "Settings", 'list_asset': "List Asset",
            'sys_pref': "System Preferences", 'lang_label': "Language / Mutauro / Inlimi",
            'apply_btn': "Apply Changes", 'display_mode': "Display Mode", 'legal_tab': "Legal Specs & Help Desk"
        },
        'sn': {
            'live_feed': "Zvigadzirwa Zviripo", 'settings': "Zvirongwa", 'list_asset': "Isa Mudziyo",
            'sys_pref': "Zvaunofarira weSisitimu", 'lang_label': "Shandura Mutauro",
            'apply_btn': "Shandura Zviripo", 'display_mode': "Chitarisiko", 'legal_tab': "Mitemo neRubatsiro"
        },
        'nd': {
            'live_feed': "Impahla Ezikhona", 'settings': "Izilungiselelo", 'list_asset': "Faka Impahla",
            'sys_pref': "Izinto ozithandayo zeSistimu", 'lang_label': "Ngena Ngolimi",
            'apply_btn': "Gcina Izinguquko", 'display_mode': "Ukukhanya", 'legal_tab': "Imithetho loSizo"
        }
    }

    active_lang_dict = translations_pool.get(current_lang, translations_pool['en'])
    active_legal_dict = faq_and_terms_matrix.get(current_lang, faq_and_terms_matrix['en'])
    
    marquee_string = " | ".join(marquee_items) if marquee_items else active_lang_dict['live_feed'] + ": Waiting for entries..."

    return {
        'ZIG_MID_RATE': usd_to_zig_mid_rate,
        'DYNAMIC_PRODUCT_MARQUEE': marquee_string,
        'PLATFORM_VERSION': "v2.0.0-Commercial",
        'TEXT': active_lang_dict,
        'LEGAL': active_legal_dict, # Dynamic legal injection
    }