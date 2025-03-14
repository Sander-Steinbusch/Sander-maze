from langchain_core.messages import SystemMessage, HumanMessage


def build_extraction_enrich_chapter_prompt(document: str) -> list[SystemMessage | HumanMessage]:
    template = (
        # persona
        "you will get a text in json format."
        "inside this json there will be an array called lineItems"
        "Every object inside this array has an element called chapter"
        "Consider this list of chapters:"
        "9-14 : Aanbrengen van colloïdaal beton"
        "9-15 : Groutscherm"
        "9-16 : Drainbuis met grindfilter t.p.v. kunstwerken"
        "9-17 : Afdichtingsplaten van geprefabriceerd gewapend beton"
        "9-18 : Bevestigingssysteem met chemische ankers"
        "9-19 : Flexibel anti-wortelscherm"
        "9-20 : Regiewerken"
        "9-21 : Kopmuren"
        "9-22 : Verholen goten in prefabbeton"
        "9-23 : Terugplaatsen van afsluitingen en muurtjes"
        "9-24 : Metalen afsluitingen met draadgaas"
        "9-25 : Metalen toegangspoort"
        "9-26 : Plaatsen van wachtkokers voor leidingen van openbaar nut"
        "9-27 : Enkelvoudige en/of meerdelige controleluiken"
        "9-28 : Metalen trappen"
        "9-29 : Leuning"
        "9-30 : Looproosters"
        "9-31 : In de grond gevormde gewapende betonwand d.m.v. secanspalen"
        "9-32 : Micropalen"
        "9-33 : Ondervangen van funderingsmuren"
        "9-34 : Het op hoogte brengen van kelderdeksel en/of roosters met metselstenen en/of ongewapend beton"
        "9-35 : Funderingsverbeteringstechnieken"
        "9-37 : Stalen damwanden"
        "9-38 : Werken voor verleggen leidingen openbaar nut"
        "9-40 : Kruising onder bestaande riolering met nieuwe buisleiding"
        "10 : Signalisatie"
        "10-1 : Verticale signalisatie en wegbebakening"
        "10-2 : Markeringen"
        "10-4 : Signalisatie van werken"
        "10-10 : Vaarwegsignalisatie"
        "10-11 : Werfsignalisatie op de vaarweg"
        "11 : Groenaanleg en groenbeheer"
        "11-2 : Grondbewerkingen"
        "11-3 : Verwerken van bodemverbeteringsmiddelen"
        "11-4 : Verwerken van meststoffen"
        "11-5 : Natuurlijke vegetatieontwikkeling"
        "11-6 : Aanleg van graslanden, wegbermen en grasmatten"
        "11-7 : Aanleg van kruidachtige vegetaties"
        "11-8 : Aanleg van houtige vegetaties"
        "11-9 : Aanleg van water-, moeras- en oeverbeplantingen"
        "11-10 : Aanleg van bij groenaanleg behorende constructies"
        "11-11 : Beheer van graslanden, wegbermen en grasmatten"
        "11-12 : Beheer van kruidachtige vegetaties"
        "11-13 : Beheer van bomen"
        "11-14 : Beheer van hagen, bosgoed en heesters"
        "11-15 : Beheer van water-, moeras-, en oeverbeplanting"
        "11-16 : Beheer van invasieve exoten"
        "11-17 : Transferten voor het verwerken van groenafval 11-17"
        "11-20 : Zandfixatie"
        "12 : Onderhouds- en Herstellingswerken"
        "12-1 : Onderhouds- en herstellingswerken aan cementbetonverhardingen"
        "12-2 : Onderhouds- en herstellingswerken aan bitumineuze verhardingen"
        "12-3 : Overlaging in cementbeton"
        "12-4 : Bitumineuze overlagingen"
        "12-5 : Bestrijkingen"
        "12-6 : Slemlagen"
        "12-7 : Bestrijking met slemafdichting"
        "12-8 : Dunne overlagingen"
        "12-9 : Ruimen van sloten"
        "12-10 : Beheer ongewenste vegetatie op (half)verhardingen"
        "12-11 : Sleufherstellingen"
        "12-12 : Ruiming en reiniging van wegen en toebehoren"
        "12-13 : Herstellen van lijnvormige elementen"
        "12-14 : Herstellen van huistoegangen"
        "13 : Werken aan Waterlopen"
        "13-1 : Onderhoud"
        "13-2 : Beschermingswerken"
        "13-10 : Vooroeververdedigingen"
        "13-11 : Penetratie met bitumineus gebonden materiaal"
        "13-12 : Penetratie met open colloïdaal beton"
        "13-13 : Betegelingen - gebonden en ongebonden"
        "13-14 : Gebonden open bekleding"
        "21 : Ontwerp, studie en berekeningsnota's"
        "21-9 : Studie van de constructie"
        "22 : Grondonderzoek"
        "22-2 : Monstername en proeven in situ"
        "22-3 : Werkplaform voor het uitvoeren van proeven in situ te water"
        "22-4 : Proeven in labo"
        "23 : Baggerwerken"
        "23-2 : Vooronderzoek"
        "23-3 : Baggeren"
        "23-4 : Vervoeren"
        "23-5 : Overname van specie"
        "23-6 : Behandelen"
        "23-7 : Bergen"
        "24 : Geotechnische constructie-elementen en constructies"
        "24-1 : Palen, putten en caissons"
        "24-2 : Damwanden"
        "24-3 : Funderingswanden"
        "24-4 : Beschoeiingen en stutwerken"
        "24-5 : Grondankers"
        "24-6 : Versnelde consolidatie"
        "24-10 : Strandhoofden"
        "24-11 : Golfbrekers"
        "24-12 : Zeedijken"
        "25 : Beton, wapening en betonconstructies"
        "25-5 : Wapening"
        "25-6 : Ter plaatse gestort beton en extra handelingen"
        "25-7 : Gesloten colloidaal beton"
        "25-8 : Geprefabriceerd beton"
        "26 : Staal en staalconstructies"
        "26-2 : Staalconstructies in constructiestaal en roestvaststaal"
        "26-3 : Lekdichtheidstest"
        "26-4 : Proefmontage van de staalconstructie"
        "26-5 : Opstellen van de staalconstructie voor bewerking door de opdrachtnemer EMU"
        "26-6 : Vervoer, lossen en opslaan op de bouwplaats van de staalconstructie"
        "26-7 : Definitieve montage op de bouwplaats van de staalconstructie"
        "30 : Hout en houten constructieonderdelen"
        "30-3 : Damwanden en beschoeiingen 250-13"
        "30-4 : Wrijfbalken en bergbalken in hout"
        "30-5 : Schotbalken in hout"
        "30-6 : Horizontale delen leuningen in hout"
        "30-7 : Aanslagbalken in hout"
        "30-8 : Hout voor sluisdeuren en stuwen"
        "30-9 : Beplanking in hout"
        "30-10 : Houten palen"
        "30-11 : Constructiebalken (voor o.a. steigers, staketsels, geleidewerken, brugdekken en leuningen)"
        "32 : Uitrustingen en aanhorigheden"
        "32-1 : Leuningen"
        "32-2 : Loopvloeren"
        "32-3 : Waterdichte deksels en luiken"
        "32-4 : Afdichtingen van voegen, voegbanden en -platen"
        "32-5 : Reddingsmaterieel"
        "32-6 : Verankeringen van stalen onderdelen in beton"
        "32-7 : Verankeringen van wapeningsstaven"
        "32-8 : Mechanische onderdelen"
        "32-9 : Schotbalken"
        "32-10 : Verkenmerken en referentieverkenmerken"
        "32-11 : Rails en wielen"
        "32-12 : Drainerend scherm achter verticale wanden"
        "32-21 : Waterdichte bedekking voor brugdekken"
        "32-31 : Brugdekvoegen"
        "32-32 : Sluitplaten"
        "32-33 : Oplegvoorzieningen"
        "32-34 : Inspectievoorzieningen"
        "32-35 : Rioleringen en afvoer van water voor kunstwerken"
        "32-36 : Taludbekleding kunstwerken"
        "32-37 : Voorzieningen voor verlichting op de brug"
        "32-38 : Vergrendelingsvoorzieningen voor beweegbare bruggen"
        "32-39 : Kabels en trekstaven"
        "32-40 : Uitbalanceren van beweegbare bruggen"
        "32-41 : Rolopleggingen en geleidingswielen"
        "1 : Algemene Administratieve Voorschriften"
        "1-4 : Administratieve voorschriften bij toepassing van het KB uitvoering"
        "2 : Algemene Bepalingen"
        "2-12 : Documenten opgemaakt door de aannemer"
        "2-13 : Organisatie van de bouwplaats"
        "2-14 : Bescherming, instandhouding en integriteit van bestaande constructies en werken"
        "4 : Voorbereidende Werken en Grondwerken"
        "4-1 : Voorbereidende werken"
        "4-2 : Grondverzet"
        "4-3 : Grondwerk voor bouwputten"
        "4-4 : Grondwerk aan onbevaarbare waterlopen"
        "4-5 : Geschikt maken zate ophoging/baanbed uitgraving"
        "4-6 : Profileren van sloten"
        "4-7 : Wapenen van bodem (hellingen/taluds)"
        "4-8 : Grondwerk ten behoeve van natuurbouw"
        "4-9 : Profileren van bermen"
        "4-10 : Verwerken van teelaarde en andere bodemsubstraten"
        "4-11 : Detecteren, opsporen en ruimen van CTE"
        "4-20 : Verlagen van het grondwaterpeil"
        "4-21 : Grondwerk ten behoeve van vooroever, strand en duin"
        "4-24 : Aanvulling met licht aanvulmateriaal"
        "5 : Onderfunderingen en Funderingen"
        "5-1 : Bescherming van de onderfundering of fundering"
        "5-2 : Wapenen van de onderfundering of fundering"
        "5-3 : Onderfunderingen"
        "5-4 : Fundering"
        "6 : Verhardingen"
        "6-1 : Cementbetonverhardingen"
        "6-2 : Bitumineuze verhardingen"
        "6-3 : Bestratingen"
        "6-4 : Andere verhardingen"
        "6-10 : Verhardingen van staalvezelgewapend beton voor een kaaiplateau"
        "7 : Rioleringen en Afvoer van Water"
        "7-1 : Riolering en afvoer van water aangelegd in een sleuf"
        "7-2 : Doorpersingen"
        "7-3 : Toegangs- en verbindingsputten"
        "7-5 : Aansluitingen op de riolering"
        "7-6 : Rioleringsonderdelen"
        "7-7 : Persleidingen"
        "7-8 : Draineringen"
        "7-9 : Opvullen van riool- en/of mantelbuizen met vloeibaar beton"
        "7-10 : Rioolrenovatie door lining met ter plaatse uitgeharde buis naadvilt door inversie"
        "7-11 : Rioolrenovatie door het aanbrengen van guniteermortel via de natte spuitmethode of handmatig"
        "aangebracht voor lokale reparaties"
        "7-12 : Rioolrenovatie door lining met ter plaatse uitgeharde buis"
        "7-13 : Rioolrenovatie door middel van buis in buissysteem met HDPE-wandversterkte buizen met gladde"
        "binnenwand"
        "7-14 : Rioolrenovatie door middel van buis in buissysteem met hard PVC wikkelbuizen"
        "7-15 : Rioolrenovatie door middel van buis in buissysteem met standaardbuizen (sliplining) met"
        "glasvezelversterkte polyesterbuizen (GVP)"
        "7-16 : Rioolrenovatie door middel van buis in buissysteem met aan de vorm aangepaste buizen"
        "(sliplining) met glasvezelversterkte polyester elementen (GVP)"
        "7-17 : Rioolrenovatie door middel van glasvezelversterkte polyester (GVP) panelen"
        "7-18 : Waterdichting door middel van injectieharsen in structuren met diameter kleiner dan of"
        "gelijk aan 800mm"
        "7-19 : Rioolrenovatie en corrosiebescherming door middel van solventvrije kunstharsen"
        "7-20 : Waterdichting door middel van injectieharsen in mantoegankelijke structuren"
        "7-21 : Herstelling van lekkende voegverbindingen en grindnesten door middel van het plaatsen van"
        "inox manchetten in buisleidingen"
        "7-22 : Rioolrenovatie met geprefabriceerde keramische elementen"
        "7-23 : Rioolrenovatie d.m.v. HDPE/grout liner"
        "7-24 : Rioolrenovatie door middel van deelrenovatie met glasvezelversterkt kunsthars"
        "7-25 : Rioolrenovatie door middel van close-fit lining met fabrieksmatig gevouwen HDPE-buizen"
        "7-26 : Rioolrenovatie door middel van pipe-bursting"
        "7-40 : Visuele onderzoeksmethoden"
        "7-41 : Schadeclassificatie van rioleringsnetten"
        "8 : Lijnvormige Elementen"
        "8-1 : Trottoirbanden (borduren), trottoirbanden-watergreppels en schampkanten"
        "8-2 : Afschermende constructies voor wegen"
        "8-3 : Ter plaatse vervaardigde en geprefabriceerde betonnen kantstroken en watergreppels"
        "8-4 : Geluidswerende constructies"
        "8-10 : Afschermende constructies"
        "9 : Allerhande Werken"
        "9-1 : Zandcement of Granulaatcement"
        "9-2 : Schraal beton"
        "9-3 : Beton"
        "9-4 : Metselwerk van metselstenen"
        "9-5 : Metselwerk van natuurstenen"
        "9-6 : Cementering van metselwerk"
        "9-7 : Bescherming van de cementering"
        "9-9 : Drainerende wandbedekking"
        "9-10 : Drainerend scherm achter verticale wanden"
        "9-11 : Drainerend scherm met dichtingsmembraan achter verticale wanden"
        "9-12 : Geprefabriceerde rechthoekige koker van gewapend beton"
        "9-13 : Voegbanden voor betonconstructies"
        "32-42 : Dempingssysteem voor voetgangersbruggen"
        "32-61 : Bolders en meerogen"
        "32-62 : Haalkommen en haalpennen"
        "32-63 : Fenders"
        "32-64 : Wrijf- en bergbalken"
        "32-65 : Beschermingsprofielen"
        "32-66 : Ladders"
        "32-67 : Geleidingsvoorzieningen"
        "32-68 : Geleidingsbeugels"
        "32-69 : Afdekplaatjes voor de grondankers"
        "32-81 : Afdichtingsprofielen en pakkingen in rubber"
        "32-82 : Aanslagbalken"
        "32-83 : Ultra hoog moleculair polyethyleen (UHMWPE)"
        "32-91 : Uitbalanceren pontons"
        "33 : Conserveringswerken"
        "33-1 : Conservering van staal"
        "33-2 : Conservering van beton"
        "33-3 : Conservering van hout"
        "34 : Herstellingswerken"
        "34-1 : Herstellen van betonconstructies"
        "34-2 : Herstellen van oevers met niet-verzakte betonnen taludplaten door opvullen van"
        "uitspoelingsholten met behulp van boor- en injectietechnieken"
        "34-3 : Herstellen van oevers met verzakte betonnen taludplaten met volledig uitgerust ponton met"
        "speciale caisson"
        "34-4 : Injecteren van holten in massieven of achter bekledingen"
        "34-5 : Injecteren van scheuren in beton"
        "34-6 : Opvijzelen en neerlaten van het brugdek"
        "35 : Indienststellingsproeven en inpassingsonderzoek"
        "35-1 : Indienststellingsproeven"
        "35-2 : Inpassingsonderzoek"
        "36 : Documentering van de uitvoering, as-builtdossier, post-interventiedossier"
        "36-2 : As-builtdossier"
        "36-3 : Post-interventiedossier"
        "46 : Leidingen"
        "46-1 : Elektrische kabels"
        "46-2 : Blazen van glasvezelkabels"
        "46-3 : Plaatsen van kabels en voerbuizen"
        "46-4 : Beheer van kabels"
        "50 : Dynamische verkeersmanagement en verkeershandhavingsstystemen"
        "50-1 : Dynamisch verkeersmanagement"
        "50-2 : Verkeershandhavingssystemen"
        "3 : Materialen"
        "3-1 : Rots"
        "3-2 : Primaire en gerecycleerde en secundaire granulaten"
        "3-3 : Grond"
        "3-4 : Afdekingsmaterialen voor bermen en taluds"
        "3-5 : Ophogings- en aanvullingsmaterialen"
        "3-6 : Bouwzand"
        "3-7 : Steenslag, rolgrind, ruwe steen en brokken puin"
        "3-8 : Cement en hydraulische bindmiddelen"
        "3-9 : Kalk"
        "3-10 : Vulstoffen en toevoegstels voor bitumineuze mengsels"
        "3-11 : Koolwaterstofproducten"
        "3-12 : Metaalproducten"
        "3-13 : Geokunststoffen (geosynthetics - geofabrics)"
        "3-14 : Banden voor diverse toepassingen"
        "3-15 : Betonoppervlakbehandelingsproducten"
        "3-16 : Voegvullingsproducten"
        "3-17 : Materialen voor voegen"
        "3-18 : Voeginlagen"
        "3-19 : Kleefvernis"
        "3-20 : Hulpstoffen en toevoegsels voor mortel en beton"
        "3-21 : Natuursteen"
        "3-22 : Calciumchloride"
        "3-23 : Bestratingselementen"
        "3-24 : Buizen en hulpstukken voor riolering en afvoer van water"
        "3-25 : Afdichtingsringen en krimpmoffen"
        "3-26 : Materialen voor draineerleidingen"
        "3-27 : Metselstenen"
        "3-28 : Draineerelementen van poreus beton"
        "3-29 : Gewapend bitumen voor afdichtingslagen"
        "3-31 : Natuurstenen trottoirbanden (borduren)"
        "3-32 : Geprefabriceerde lijnvormige elementen van beton voor wegenbouw"
        "3-33 : Geprefabriceerde betonnen toegangs- en verbindingsputten"
        "3-34 : Geprefabriceerde gewapende betonnen polygonale segmenten voor afzinkputten"
        "3-35 : Geprefabriceerde grestoegangs- of verbindingsput"
        "3-36 : Kunststof toegangs- en verbindingsputten"
        "3-37 : Geprefabriceerde rechthoekige koker van gewapend beton"
        "3-38 : Geprefabriceerde huisaansluitputjes"
        "3-40 : Geprefabriceerde betonnen bakken voor straat- of trottoirkolken"
        "3-41 : Geprefabriceerde kop- en keermuren van gewapend beton"
        "3-42 : Taludgoten, begin- en eindstukken van beton"
        "3-43 : Bekleding van betonbuizen en toegangs- of verbindingsputten"
        "3-44 : Kunsthars"
        "3-45 : Glasvezelversterkte kunststoffen"
        "3-46 : Glasvezelversterkte betonnen schaaldelen"
        "3-47 : Geprefabriceerde profielelementen"
        "3-48 : Geprefabriceerde betonelementen voor drainerende talud- en/of bodembekleding"
        "3-49 : Geprefabriceerde betonelementen voor teenversterking en damwanden"
        "3-50 : Houten elementen voor teen- en taludversterkingen"
        "3-51 : Geprefabriceerde betonnen afvoergoten met metalen rooster"
        "3-52 : Betonzuilen voor taludbescherming"
        "3-53 : Coating voor verkeerstekens"
        "3-54 : Bekledingsmateriaal voor niet-inwendig verlichte verkeersborden"
        "3-55 : Sokkels voor verkeerstekens"
        "3-56 : Chemische verankeringen"
        "3-57 : Colloïdaal beton"
        "3-58 : Geprefabriceerde gewapend betonnen afsluitplaten"
        "3-59 : Trottoirpaaltjes"
        "3-61 : Meststoffen"
        "3-62 : Bodemverbeteringsmiddelen"
        "3-63 : Zaden"
        "3-64 : Graszoden"
        "3-65 : Materialen voor boomsteunen"
        "3-66 : Houtachtige gewassen"
        "3-67 : Kruidachtige vegetaties"
        "3-68 : Water- en oeverplanten"
        "3-69 : Biologisch afbreekbare geotextielen"
        "3-70 : Rioolrenovatieproducten"
        "3-71 : Droge hydraulische mortel"
        "3-72 : Geprefabriceerde gewapende betonnen polygonale of cirkelvormige segmenten voor afzinkputten"
        "3-73 : Metsel- en pleistermortel"
        "3-74 : Sneldrogende voegmortel"
        "3-75 : Biologisch afbreekbare, niet houtige elementen voor teen- en taludversterkingen"
        "3-76 : Bevestigingsmiddelen voor erosiewerende elementen"
        "3-77 : Materialen voor wortelruimte onder een verharding"
        "3-78 : Mobiele afsluiting"
        "3-79 : Grondwaterpeilbuizen"
        "3-80 : Boomplaten"
        "3-81 : Beschermingselement voor aanplantingen"
        "3-82 : Afschermende constructies"
        "3-83 : Wortelgeleidingsplaten"
        "3-84 : Krimpgecompenseerde aangietmortels"
        "3-85 : Kunstmatige gietrand"
        "3-86 : Zelfverdichtend beton"
        "47 : Processturingen"
        "47-1 : PLC"
        "48a : Teletechniek"
        "48b : Afstandsbewaking en besturing"
        "48c : Telematicatoepassingen"
        "48d : Telematica security"
        "48a-1 : Gebruik van het telematica IP netwerk"
        "48a-2 : Gebruik van het transportnetwerk"
        "48b-2 : Projectmatige eisen"
        "48b-3 : Generieke technische eisen"
        "48b-4 : Specifieke applicaties"
        "48c-1 : Projectmatige eisen"
        "48c-2 : Generieke technische eisen"
        "48c-3 : Specifieke applicaties"
        "48d-1 : ICT- en informatiebeveiligingsbeleid"
        "48d-2 : Speciefieke beveiligingsmaatregelen"
        "49 : Verlichting"
        "49-1 : Lampen"
        "49-2 : Voorschakelapparatuur"
        "49-3 : Verlichtingstoestellen"
        "49-4 : Lichtmasten"
        "49-5 : Besturing, bediening en bewaking van wegverlichtingsinstallaties"
        "51 : Overige systemen langs wegen"
        "52 : Systemen langs waterwegen"
        "53 : Tunnels"
        "51-1 : Lichtseininstallaties"
        "51-2 : Inwendig verlichte signaalborden"
        "51-3 : Afbakening"
        "51-4 : Steunen voor signaleringsinstallaties"
        "51-5 : Meet, detectie en monitoring apparatuur"
        "52-2 : Seinlantaarns"
        "52-3 : Peilmetingen en peildetecties"
        "52-4 : Elektische slagbomen"
        "53-1 : Elektromechanische installaties"
        "41 : Mechanica algemeen"
        "42 : Elektrische machines en apparatuur"
        "43 : Werkingsprincipes van beweegbare kunstwerken"
        "44 : Oleohydraulica"
        "45 : Waterhydraulica"
        "45-2 : Pompen"
        "45-3 : Appendages"
        "45-4 : Leidingen"
        "44-2 : Constructieve schikkingen"
        "43-2 : Beweegbare bruggen"
        "43-3 : Sluizen"
        "43-4 : Stuwen"
        "42-2 : Driefasige vermogentransformatoren"
        "42-3 : Motoren"
        "42-4 : Stroomvoorzieningen"
        "42-5 : Hoogspanningscabines"
        "42-6 : Laagspanningsschakelinrichtingen"
        "42-7 : Overigeapparatuur"
        "41-2 : Ontwerp"
        "41-3 : Uitvoering"
        "41-4 : Aandrijf- en afremelementen"
        "41-5 : Overbrengingselementen"
        "41-6 : Ophangings-, bedienings- en geleidingselementen"
        "41-7 : Bevestigingselementen"
        "41-8 : Beschermingselementen"
        "41-9 : Smering"
        "3-87 : Geluidswerende constructies"
        "3-88 : Bodemafdekkende middelen"
        "3-90 : Markeringsproducten"
        "3-91 : Glasparels en stroefmakende middelen voor markeringsproducten"
        "3-93 : Kunststofladders"
        "3-94 : Looproosterelementen"
        "3-95 : Metalen afsluiting met draadgaas"
        "3-96 : Metalen toegangspoort"
        "3-97 : Kunststofinfiltratiekratten"
        "DIV1 : Diverse 1"
        "\n"
        "going on the basis of what's inside each object, which of these lines does fit the best?"
        "If the information inside the object is not sufficient enough, cross reference the item description with the author inside the basis object."
        "Add your answer to the chapter element of each object."
        "If you don't know the answer, don't add anything"
        "leave out the JSON markdown and answer in one JSON object including all the previous data"
    )

    return [
        SystemMessage(
            content=template
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": document},

            ]
        )
    ]
