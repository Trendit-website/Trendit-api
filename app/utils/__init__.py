'''
This package contains utilities for the Trendit³ Flask application.


@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import requests
from flask import jsonify

class AppJSON:
    
    naija_states = {
        "states": [
			{
			"name": "Abia State",
			"local_governments": [
				"Aba North",
				"Aba South",
				"Arochukwu",
				"Bende",
				"Ikwuano",
				"Isiala Ngwa North",
				"Isiala Ngwa South",
				"Isuikwuato",
				"Obi Ngwa",
				"Ohafia",
				"Osisioma Ngwa",
				"Ugwunagbo",
				"Ukwa East",
				"Ukwa West",
				"Umuahia North",
				"Umuahia South",
				"Umu Nneochi"
			]
			},
			{
			"name": "Adamawa State",
			"local_governments": [
				"Demsa",
				"Fufore",
				"Ganye",
				"Girei",
				"Gombi",
				"Guyuk",
				"Hong",
				"Jada",
				"Lamurde",
				"Madagali",
				"Maiha",
				"Mayo-Belwa",
				"Michika",
				"Mubi North",
				"Mubi South",
				"Numan",
				"Shelleng",
				"Song",
				"Toungo",
				"Yola North",
				"Yola South"
			]
			},
			{
			"name": "Akwa Ibom State",
			"local_governments": [
				"Abak",
				"Eastern Obolo",
				"Eket",
				"Esit Eket",
				"Essien Udim",
				"Etim Ekpo",
				"Etinan",
				"Ibeno",
				"Ibesikpo Asutan",
				"Ibiono-Ibom",
				"Ika",
				"Ikono",
				"Ikot Abasi",
				"Ikot Ekpene",
				"Ini",
				"Itu",
				"Mbo",
				"Mkpat-Enin",
				"Nsit-Atai",
				"Nsit-Ibom",
				"Nsit-Ubium",
				"Obot Akara",
				"Okobo",
				"Onna",
				"Oron",
				"Oruk Anam",
				"Udung-Uko",
				"Ukanafun",
				"Uruan",
				"Urue-Offong/Oruko",
				"Uyo"
			]
			},
			{
			"name": "Anambra State",
			"local_governments": [
				"Aguata",
				"Anambra East",
				"Anambra West",
				"Anaocha",
				"Awka North",
				"Awka South",
				"Ayamelum",
				"Dunukofia",
				"Ekwusigo",
				"Idemili North",
				"Idemili South",
				"Ihiala",
				"Njikoka",
				"Nnewi North",
				"Nnewi South",
				"Ogbaru",
				"Onitsha North",
				"Onitsha South",
				"Orumba North",
				"Orumba South",
				"Oyi"
			]
			},
			{
			"name": "Bauchi State",
			"local_governments": [
				"Alkaleri",
				"Bauchi",
				"Bogoro",
				"Damban",
				"Darazo",
				"Dass",
				"Ganjuwa",
				"Giade",
				"Itas/Gadau",
				"Jama'are",
				"Katagum",
				"Kirfi",
				"Misau",
				"Ningi",
				"Shira",
				"Tafawa Balewa",
				"Toro",
				"Warji",
				"Zaki"
			]
			},
			{
			"name": "Bayelsa State",
			"local_governments": [
				"Brass",
				"Ekeremor",
				"Kolokuma/Opokuma",
				"Nembe",
				"Ogbia",
				"Sagbama",
				"Southern Ijaw",
				"Yenagoa"
			]
			},
			{
			"name": "Benue State",
			"local_governments": [
				"Ado",
				"Agatu",
				"Apa",
				"Buruku",
				"Gboko",
				"Guma",
				"Gwer East",
				"Gwer West",
				"Katsina-Ala",
				"Konshisha",
				"Kwande",
				"Logo",
				"Makurdi",
				"Obi",
				"Ogbadibo",
				"Ohimini",
				"Oju",
				"Okpokwu",
				"Oturkpo",
				"Tarka",
				"Ukum",
				"Ushongo",
				"Vandeikya"
			]
			},
			{
			"name": "Borno State",
			"local_governments": [
				"Abadam",
				"Askira/Uba",
				"Bama",
				"Bayo",
				"Biu",
				"Chibok",
				"Damboa",
				"Dikwa",
				"Gubio",
				"Guzamala",
				"Gwoza",
				"Hawul",
				"Jere",
				"Kaga",
				"Kala/Balge",
				"Konduga",
				"Kukawa",
				"Kwaya Kusar",
				"Mafa",
				"Magumeri",
				"Maiduguri",
				"Marte",
				"Mobbar",
				"Monguno",
				"Ngala",
				"Nganzai",
				"Shani"
			]
			},
			{
			"name": "Cross River State",
			"local_governments": [
				"Akpabuyo",
				"Akpamkpa",
				"Bakassi",
				"Bekwarra",
				"Biase",
				"Boki",
				"Calabar Municipal",
				"Calabar South",
				"Etung",
				"Ikom",
				"Obanliku",
				"Obubra",
				"Obudu",
				"Odukpani",
				"Ogoja",
				"Yakuur",
				"Yala"
			]
			},
			{
			"name": "Delta State",
			"local_governments": [
				"Aniocha North",
				"Aniocha South",
				"Bomadi",
				"Burutu",
				"Ethiope East",
				"Ethiope West",
				"Ika North East",
				"Ika South",
				"Isoko North",
				"Isoko South",
				"Ndokwa East",
				"Ndokwa West",
				"Okpe",
				"Oshimili North",
				"Oshimili South",
				"Patani",
				"Sapele",
				"Udu",
				"Ughelli North",
				"Ughelli South",
				"Ukwuani",
				"Uvwie",
				"Warri North",
				"Warri South",
				"Warri South West"
			]
			},
			{
			"name": "Ebonyi State",
			"local_governments": [
				"Abakaliki",
				"Afikpo North",
				"Afikpo South (Edda)",
				"Ebonyi",
				"Ezza North",
				"Ezza South",
				"Ikwo",
				"Ishielu",
				"Ivo",
				"Izzi",
				"Ohaozara",
				"Ohaukwu",
				"Onicha"
			]
			},
			{
			"name": "Edo State",
			"local_governments": [
				"Akoko-Edo",
				"Egor",
				"Esan Central",
				"Esan North-East",
				"Esan South-East",
				"Esan West",
				"Etsako Central",
				"Etsako East",
				"Etsako West",
				"Igueben",
				"Ikpoba Okha",
				"Oredo",
				"Orhionmwon",
				"Ovia North-East",
				"Ovia South-West",
				"Owan East",
				"Owan West",
				"Uhunmwonde"
			]
			},
			{
			"name": "Ekiti State",
			"local_governments": [
				"Ado Ekiti",
				"Efon",
				"Ekiti East",
				"Ekiti South-West",
				"Ekiti West",
				"Emure",
				"Gbonyin",
				"Ido Osi",
				"Ijero",
				"Ikere",
				"Ikole",
				"Ilejemeje",
				"Irepodun/Ifelodun",
				"Ise/Orun",
				"Moba",
				"Oye"
			]
			},
			{
			"name": "Enugu State",
			"local_governments": [
				"Aninri",
				"Awgu",
				"Enugu East",
				"Enugu North",
				"Enugu South",
				"Ezeagu",
				"Igbo Etiti",
				"Igbo Eze North",
				"Igbo Eze South",
				"Isi Uzo",
				"Nkanu East",
				"Nkanu West",
				"Nsukka",
				"Oji River",
				"Udenu",
				"Udi",
				"Uzo-Uwani"
			]
			},
			{
			"name": "Gombe State",
			"local_governments": [
				"Akko",
				"Balanga",
				"Billiri",
				"Dukku",
				"Funakaye",
				"Gombe",
				"Kaltungo",
				"Kwami",
				"Nafada",
				"Shongom",
				"Yamaltu/Deba"
			]
			},
			{
			"name": "Imo State",
			"local_governments": [
				"Aboh Mbaise",
				"Ahiazu Mbaise",
				"Ehime Mbano",
				"Ezinihitte",
				"Ideato North",
				"Ideato South",
				"Ihitte/Uboma",
				"Ikeduru",
				"Isiala Mbano",
				"Isu",
				"Mbaitoli",
				"Ngor Okpala",
				"Njaba",
				"Nkwerre",
				"Nwangele",
				"Obowo",
				"Oguta",
				"Ohaji/Egbema",
				"Okigwe",
				"Orlu",
				"Orsu",
				"Oru East",
				"Oru West",
				"Owerri Municipal",
				"Owerri North",
				"Owerri West",
				"Unuimo"
			]
			},
			{
			"name": "Jigawa State",
			"local_governments": [
				"Auyo",
				"Babura",
				"Biriniwa",
				"Birnin Kudu",
				"Buji",
				"Dutse",
				"Gagarawa",
				"Garki",
				"Gumel",
				"Guri",
				"Gwaram",
				"Gwiwa",
				"Hadejia",
				"Jahun",
				"Kafin Hausa",
				"Kaugama",
				"Kazaure",
				"Kiri Kasama",
				"Kiyawa",
				"Kaugama",
				"Maigatari",
				"Malam Madori",
				"Miga",
				"Ringim",
				"Roni",
				"Sule Tankarkar",
				"Taura",
				"Yankwashi"
			]
			},
			{
			"name": "Kaduna State",
			"local_governments": [
				"Birnin Gwari",
				"Chikun",
				"Giwa",
				"Igabi",
				"Ikara",
				"Jaba",
				"Jema'a",
				"Kachia",
				"Kaduna North",
				"Kaduna South",
				"Kagarko",
				"Kajuru",
				"Kaura",
				"Kauru",
				"Kubau",
				"Kudan",
				"Lere",
				"Makarfi",
				"Sabon Gari",
				"Sanga",
				"Soba",
				"Zangon Kataf",
				"Zaria"
			]
			},
			{
			"name": "Kano State",
			"local_governments": [
				"Ajingi",
				"Albasu",
				"Bagwai",
				"Bebeji",
				"Bichi",
				"Bunkure",
				"Dala",
				"Dambatta",
				"Dawakin Kudu",
				"Dawakin Tofa",
				"Doguwa",
				"Fagge",
				"Gabasawa",
				"Garko",
				"Garun Mallam",
				"Gaya",
				"Gezawa",
				"Gwale",
				"Gwarzo",
				"Kabo",
				"Kano Municipal",
				"Karaye",
				"Kibiya",
				"Kiru",
				"Kumbotso",
				"Kunchi",
				"Kura",
				"Madobi",
				"Makoda",
				"Minjibir",
				"Nasarawa",
				"Rano",
				"Rimin Gado",
				"Rogo",
				"Shanono",
				"Sumaila",
				"Takai",
				"Tarauni",
				"Tofa",
				"Tsanyawa",
				"Tudun Wada",
				"Ungogo",
				"Warawa",
				"Wudil"
			]
			},
			{
			"name": "Katsina State",
			"local_governments": [
				"Bakori",
				"Batagarawa",
				"Batsari",
				"Baure",
				"Bindawa",
				"Charanchi",
				"Dan Musa",
				"Dandume",
				"Danja",
				"Daura",
				"Dutsi",
				"Dutsin Ma",
				"Faskari",
				"Funtua",
				"Ingawa",
				"Jibia",
				"Kafur",
				"Kaita",
				"Kankara",
				"Kankia",
				"Katsina",
				"Kurfi",
				"Kusada",
				"Mai'Adua",
				"Malumfashi",
				"Mani",
				"Mashi",
				"Matazu",
				"Musawa",
				"Rimi",
				"Sabuwa",
				"Safana",
				"Sandamu",
				"Zango"
			]
			},
			{
			"name": "Kebbi State",
			"local_governments": [
				"Aleiro",
				"Arewa Dandi",
				"Argungu",
				"Augie",
				"Bagudo",
				"Birnin Kebbi",
				"Bunza",
				"Dandi",
				"Fakai",
				"Gwandu",
				"Jega",
				"Kalgo",
				"Koko/Besse",
				"Maiyama",
				"Ngaski",
				"Sakaba",
				"Shanga",
				"Suru",
				"Wasagu/Danko",
				"Yauri",
				"Zuru"
			]
			},
			{
			"name": "Kogi State",
			"local_governments": [
				"Adavi",
				"Ajaokuta",
				"Ankpa",
				"Bassa",
				"Dekina",
				"Ibaji",
				"Idah",
				"Igalamela-Odolu",
				"Ijumu",
				"Kabba/Bunu",
				"Kogi",
				"Lokoja",
				"Mopa-Muro",
				"Ofu",
				"Ogori/Magongo",
				"Okehi",
				"Okene",
				"Olamaboro",
				"Omala",
				"Yagba East",
				"Yagba West"
			]
			},
			{
			"name": "Kwara State",
			"local_governments": [
				"Asa",
				"Baruten",
				"Edu",
				"Ekiti",
				"Ifelodun",
				"Ilorin East",
				"Ilorin South",
				"Ilorin West",
				"Irepodun",
				"Isin",
				"Kaiama",
				"Moro",
				"Offa",
				"Oke Ero",
				"Oyun",
				"Pategi"
			]
			},
			{
			"name": "Lagos State",
			"local_governments": [
				"Agege",
				"Ajeromi-Ifelodun",
				"Alimosho",
				"Amuwo-Odofin",
				"Apapa",
				"Badagry",
				"Epe",
				"Eti-Osa",
				"Ibeju-Lekki",
				"Ifako-Ijaiye",
				"Ikeja",
				"Ikorodu",
				"Kosofe",
				"Lagos Island",
				"Lagos Mainland",
				"Mushin",
				"Ojo",
				"Oshodi-Isolo",
				"Shomolu",
				"Surulere"
			]
			},
			{
			"name": "Nasarawa State",
			"local_governments": [
				"Akwanga",
				"Awe",
				"Doma",
				"Karu",
				"Keana",
				"Keffi",
				"Kokona",
				"Lafia",
				"Nasarawa",
				"Nasarawa Egon",
				"Obi",
				"Toto",
				"Wamba"
			]
			},
			{
			"name": "Niger State",
			"local_governments": [
				"Agaie",
				"Agwara",
				"Bida",
				"Borgu",
				"Bosso",
				"Chanchaga",
				"Edati",
				"Gbako",
				"Gurara",
				"Katcha",
				"Kontagora",
				"Lapai",
				"Lavun",
				"Magama",
				"Mariga",
				"Mashegu",
				"Mokwa",
				"Munya",
				"Paikoro",
				"Rafi",
				"Rijau",
				"Shiroro",
				"Suleja",
				"Tafa",
				"Wushishi"
			]
			},
			{
			"name": "Ogun State",
			"local_governments": [
				"Abeokuta North",
				"Abeokuta South",
				"Ado-Odo/Ota",
				"Egbado North",
				"Egbado South",
				"Ewekoro",
				"Ifo",
				"Ijebu East",
				"Ijebu North",
				"Ijebu North East",
				"Ijebu Ode",
				"Ikenne",
				"Imeko Afon",
				"Ipokia",
				"Obafemi Owode",
				"Odeda",
				"Odogbolu",
				"Ogun Waterside",
				"Remo North",
				"Shagamu"
			]
			},
			{
			"name": "Ondo State",
			"local_governments": [
				"Akoko North-East",
				"Akoko North-West",
				"Akoko South-East",
				"Akoko South-West",
				"Akure North",
				"Akure South",
				"Ese Odo",
				"Idanre",
				"Ifedore",
				"Ilaje",
				"Ile Oluji/Okeigbo",
				"Irele",
				"Odigbo",
				"Okitipupa",
				"Ondo East",
				"Ondo West",
				"Ose",
				"Owo"
			]
			},
			{
			"name": "Osun State",
			"local_governments": [
				"Aiyedaade",
				"Aiyedire",
				"Atakunmosa East",
				"Atakunmosa West",
				"Boluwaduro",
				"Boripe",
				"Ede North",
				"Ede South",
				"Egbedore",
				"Ejigbo",
				"Ife Central",
				"Ife East",
				"Ife North",
				"Ife South",
				"Ifedayo",
				"Ifelodun",
				"Ila",
				"Ilesa East",
				"Ilesa West",
				"Irepodun",
				"Irewole",
				"Isokan",
				"Iwo",
				"Obokun",
				"Odo Otin",
				"Ola Oluwa",
				"Olorunda",
				"Oriade",
				"Orolu",
				"Osogbo"
			]
			},
			{
			"name": "Oyo State",
			"local_governments": [
				"Afijio",
				"Akinyele",
				"Atiba",
				"Atisbo",
				"Egbeda",
				"Ibadan North",
				"Ibadan North-East",
				"Ibadan North-West",
				"Ibadan South-East",
				"Ibadan South-West",
				"Ibarapa Central",
				"Ibarapa East",
				"Ibarapa North",
				"Ido",
				"Ifedapo",
				"Irepo",
				"Iseyin",
				"Itesiwaju",
				"Iwajowa",
				"Kajola",
				"Lagelu",
				"Ogbomosho North",
				"Ogbomosho South",
				"Ogo Oluwa",
				"Olorunsogo",
				"Oluyole",
				"Ona Ara",
				"Orelope",
				"Ori Ire",
				"Oyo",
				"Oyo East",
				"Saki East",
				"Saki West",
				"Surulere"
			]
			},
			{
			"name": "Plateau State",
			"local_governments": [
				"Barkin Ladi",
				"Bassa",
				"Bokkos",
				"Jos East",
				"Jos North",
				"Jos South",
				"Kanam",
				"Kanke",
				"Langtang North",
				"Langtang South",
				"Mangu",
				"Mikang",
				"Pankshin",
				"Qua'an Pan",
				"Riyom",
				"Shendam",
				"Wase"
			]
			},
			{
			"name": "Rivers State",
			"local_governments": [
				"Abua/Odual",
				"Ahoada East",
				"Ahoada West",
				"Akuku-Toru",
				"Andoni",
				"Asari-Toru",
				"Bonny",
				"Degema",
				"Emuoha",
				"Eleme",
				"Etche",
				"Gokana",
				"Ikwerre",
				"Khana",
				"Obio/Akpor",
				"Ogba/Egbema/Ndoni",
				"Ogu/Bolo",
				"Okrika",
				"Omuma",
				"Opobo/Nkoro",
				"Oyigbo",
				"Port Harcourt",
				"Tai"
			]
			},
			{
			"name": "Sokoto State",
			"local_governments": [
				"Binji",
				"Bodinga",
				"Dange Shuni",
				"Gada",
				"Goronyo",
				"Gudu",
				"Gwadabawa",
				"Illela",
				"Isa",
				"Kebbe",
				"Kware",
				"Rabah",
				"Sabon Birni",
				"Shagari",
				"Silame",
				"Sokoto North",
				"Sokoto South",
				"Tambuwal",
				"Tangaza",
				"Tureta",
				"Wamako",
				"Wurno",
				"Yabo"
			]
			},
			{
			"name": "Taraba State",
			"local_governments": [
				"Ardo Kola",
				"Bali",
				"Donga",
				"Gashaka",
				"Gassol",
				"Ibi",
				"Jalingo",
				"Karim Lamido",
				"Kumi",
				"Lau",
				"Sardauna",
				"Takum",
				"Ussa",
				"Wukari",
				"Yorro",
				"Zing"
			]
			},
			{
			"name": "Yobe State",
			"local_governments": [
				"Bade",
				"Bursari",
				"Damaturu",
				"Fika",
				"Fune",
				"Geidam",
				"Gujba",
				"Gulani",
				"Jakusko",
				"Karasuwa",
				"Machina",
				"Nangere",
				"Nguru",
				"Potiskum",
				"Tarmuwa",
				"Yunusari",
				"Yusufari"
			]
			},
			{
			"name": "Zamfara State",
			"local_governments": [
				"Anka",
				"Bakura",
				"Birnin Magaji/Kiyaw",
				"Bukkuyum",
				"Bungudu",
				"Chafe",
				"Gummi",
				"Gusau",
				"Kaura Namoda",
				"Maradun",
				"Maru",
				"Shinkafi",
				"Talata Mafara",
				"Tsafe",
				"Zurmi"
			]
			},
			{
			"name": "Federal Capital Territory State",
			"local_governments": [
				"Abaji",
				"Abuja Municipal",
				"Bwari",
				"Gwagwalada",
				"Kuje",
				"Kwali",
			]
			},
		]
    }
    
    @classmethod
    def get_states(cls):
        naija_states = cls.naija_states
        return [state['name'] for state in naija_states['states']]

    @classmethod
    def get_local_governments(cls, state_name):
        naija_states = cls.naija_states
        for state in naija_states['states']:
            if state['name'].lower() == state_name.lower():
                return state['local_governments']
        return []
    
    @classmethod
    def get_state_for_local_government(cls, lg_name):
        naija_states = cls.naija_states
        for state in naija_states['states']:
            if lg_name in state['local_governments']:
                return state['name']
        return None

    @classmethod
    def state_exists(cls, state_name):
        naija_states = cls.naija_states
        return state_name in [state['name'] for state in naija_states['states']]
    
    @classmethod
    def local_government_exists(cls, lg_name):
        naija_states = cls.naija_states
        for state in naija_states['states']:
            if lg_name in state['local_governments']:
                return True
        return False

    @classmethod
    def get_num_states(cls):
        naija_states = cls.naija_states
        return len(naija_states['states'])

    @classmethod
    def get_states_with_local_gov_count(cls, count):
        naija_states = cls.naija_states
        states_with_count = []
        for state in naija_states['states']:
            if len(state['local_governments']) == count:
                states_with_count.append(state['name'])
        return states_with_count
    
    # Example usage:
    #print(AppJSON.get_states())
    #print(AppJSON.get_local_governments("Lagos"))
    #print(AppJSON.get_state_for_local_government("Yaba"))
    #print(AppJSON.state_exists("Kano"))
    #print(AppJSON.local_government_exists("Ikeja"))
    #print(AppJSON.get_num_states())
    #print(AppJSON.get_states_with_local_gov_count(10))