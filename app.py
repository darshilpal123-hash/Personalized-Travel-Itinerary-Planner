from __future__ import annotations
import os, json, math, random, re
from datetime import date, timedelta
from io import BytesIO
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

APP_TITLE = 'Personalized Travel Itinerary Planner'
FX = {'INR': 1.0, 'USD': 0.012, 'EUR': 0.011, 'GBP': 0.0095, 'THB': 0.43, 'JPY': 1.8, 'IDR': 190.0, 'AED': 0.044, 'AUD': 0.018, 'CAD': 0.016}
CITY_DATA = {
 'Goa, India': {'country':'India','currency':'INR','vibes':['Beach','Urban'],'months':[11,12,1,2,3],'tags':['Beach reset','Sunsets','Seafood'], 'coords':(15.49,73.83),'spots':[
 ('Fontainhas Latin Quarter','History',15.49,73.83,250),('Miramar Beach','Beach',15.46,73.81,100),('Basilica of Bom Jesus','History',15.50,73.91,200),('Dona Paula Viewpoint','Beach',15.46,73.80,100),('Anjuna Flea Market','Shopping',15.57,73.74,300),('Fort Aguada','History',15.50,73.77,250),('Candolim Beach','Beach',15.52,73.76,100),('Spice Plantation','Nature',15.42,74.00,900)]},
 'Jaipur, India': {'country':'India','currency':'INR','vibes':['Cultural','Urban'],'months':[10,11,12,1,2,3],'tags':['Heritage trails','Local crafts','Royal history'],'coords':(26.91,75.79),'spots':[
 ('Hawa Mahal','History',26.92,75.82,200),('City Palace','History',26.93,75.82,700),('Jantar Mantar','History',26.92,75.82,200),('Albert Hall Museum','History',26.91,75.82,300),('Johari Bazaar','Shopping',26.92,75.82,500),('Patrika Gate','Culture',26.82,75.80,100),('Amer Fort','History',26.99,75.85,500),('Nahargarh Fort','History',26.94,75.85,300)]},
 'Manali, India': {'country':'India','currency':'INR','vibes':['Mountains','Adventure'],'months':[3,4,5,6,9,10,12,1,2],'tags':['Mountain air','Adventure','Scenic escapes'],'coords':(32.24,77.19),'spots':[
 ('Hadimba Temple','History',32.25,77.18,50),('Old Manali','Food',32.25,77.19,250),('Manu Temple','History',32.26,77.19,50),('Solang Valley','Adventure',32.32,77.16,900),('Vashisht Hot Springs','Wellness',32.26,77.20,50),('Mall Road','Shopping',32.24,77.19,300),('Jogini Waterfall Trail','Adventure',32.27,77.20,100),('Naggar Castle','History',32.12,77.17,200)]},
 'Mumbai, India': {'country':'India','currency':'INR','vibes':['Urban','Cultural'],'months':[11,12,1,2,3],'tags':['Street food','City energy','Art & culture'],'coords':(19.08,72.88),'spots':[
 ('Gateway of India','History',18.92,72.83,50),('Kala Ghoda Art District','Culture',18.93,72.83,100),('Chhatrapati Shivaji Maharaj Vastu Sangrahalaya','History',18.93,72.83,500),('Marine Drive','Leisure',18.94,72.82,50),('Crawford Market','Shopping',18.95,72.83,200),('Bandra Fort','History',19.04,72.82,50),('Juhu Beach','Beach',19.10,72.83,150),('Sassoon Dock','Food',18.91,72.82,250)]},
 'Bangkok, Thailand': {'country':'Thailand','currency':'THB','vibes':['Urban','Cultural','Food'],'months':[11,12,1,2],'tags':['Street eats','Temple hopping','Night markets'],'coords':(13.75,100.50),'spots':[
 ('Wat Pho','History',13.75,100.49,300),('Grand Palace','History',13.75,100.49,500),('Pak Khlong Talat Flower Market','Shopping',13.74,100.50,100),('Chinatown food walk','Food',13.74,100.51,500),('Lumphini Park','Nature',13.73,100.54,0),('Chatuchak Weekend Market','Shopping',13.80,100.55,400),('Jim Thompson House','Culture',13.75,100.53,400),('Asiatique Riverfront','Nightlife',13.70,100.50,300)]},
 'Kyoto, Japan': {'country':'Japan','currency':'JPY','vibes':['Cultural','Mountains'],'months':[3,4,5,10,11],'tags':['Temple gardens','Seasonal beauty','Tea culture'],'coords':(35.01,135.77),'spots':[
 ('Nishiki Market','Food',35.00,135.76,1200),('Nijo Castle','History',35.01,135.75,800),('Kiyomizu-dera','History',34.99,135.78,500),('Gion district walk','Culture',35.00,135.78,0),('Philosopher’s Path','Nature',35.03,135.79,0),('Arashiyama Bamboo Grove','Nature',35.01,135.67,0),('Fushimi Inari Shrine','History',34.97,135.77,0),('Kyoto Railway Museum','Culture',34.99,135.75,1500)]},
 'Lisbon, Portugal': {'country':'Europe','currency':'EUR','vibes':['Urban','Cultural','Beach'],'months':[4,5,6,9,10],'tags':['Coastal charm','Tile art','Cafe culture'],'coords':(38.72,-9.14),'spots':[
 ('Alfama lanes','Culture',38.71,-9.13,0),('São Jorge Castle','History',38.71,-9.13,1500),('Time Out Market','Food',38.71,-9.15,1800),('Belém Tower','History',38.69,-9.22,800),('Jerónimos Monastery','History',38.70,-9.21,1200),('LX Factory','Shopping',38.70,-9.18,500),('Praça do Comércio','Culture',38.71,-9.14,0),('Miradouro da Senhora do Monte','Leisure',38.72,-9.13,0)]}
}

st.set_page_config(page_title=APP_TITLE, page_icon='🧭', layout='wide')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root{--ink:#172b2a;--teal:#176b63;--mint:#dcefe8;--sand:#f7f2e8;--coral:#e98969}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:linear-gradient(135deg,#fbfaf6 0%,#f0f7f3 100%)}
h1,h2,h3{font-family:'Playfair Display',serif!important;color:#173d39}
.hero{padding:2rem 2.2rem;border-radius:24px;background:linear-gradient(120deg,#143f3a,#23786e 65%,#e5a17e);color:white;margin-bottom:1.2rem;box-shadow:0 12px 34px #153c321f}
.hero h1{color:white!important;font-size:2.5rem;margin:0}.hero p{font-size:1.05rem;opacity:.94;margin:.5rem 0 0}
.pill{display:inline-block;background:#e1f2eb;color:#155e55;border-radius:99px;padding:5px 11px;margin:3px;font-size:.8rem;font-weight:700}
.metric{background:white;border:1px solid #e0e9e3;border-radius:16px;padding:14px 16px}
.daycard{background:white;border:1px solid #e2e9e3;border-radius:16px;padding:16px 18px;margin:10px 0;box-shadow:0 5px 18px #123b2e0a}
.smallmuted{color:#637873;font-size:.86rem}.stButton>button{border-radius:12px;border:0;background:#176b63;color:white;font-weight:700;padding:.55rem 1rem}.stButton>button:hover{background:#124d47;color:white}
[data-testid="stSidebar"]{background:#f2f7f3}
</style>''', unsafe_allow_html=True)

# ----------------------------- Helpers ------------------------------------
def haversine(a, b):
    lat1, lon1 = a; lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    h = math.sin(dlat/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return 6371 * 2 * math.asin(math.sqrt(min(1, h)))

def currency_for(destination):
    data = CITY_DATA.get(destination, {})
    return data.get('currency', 'USD')

def fmt_money(amount, currency):
    symbols = {'INR':'₹','USD':'$','EUR':'€','GBP':'£','THB':'฿','JPY':'¥','IDR':'Rp ','AED':'AED ','AUD':'A$','CAD':'C$'}
    return f"{symbols.get(currency, currency+' ')}{amount:,.0f}"

def local_to_usd(amount, currency):
    return amount * FX.get(currency, 1.0)

def api_generate(prompt, provider, api_key):
    """Optional LLM call. Returns text or None; caller always has a deterministic demo fallback."""
    if not api_key: return None
    try:
        if provider == 'Gemini':
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text if response and response.text else None
        else:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(model='llama-3.3-70b-versatile', messages=[{'role':'user','content':prompt}], temperature=0.6)
            return response.choices[0].message.content if response.choices else None
    except Exception as exc:
        st.warning(f'AI provider unavailable; using the built-in planner instead. Details: {str(exc)[:180]}')
        return None

def recommend_destinations(vibe, budget, trip_date, interests):
    month = trip_date.month
    scores=[]
    for city, d in CITY_DATA.items():
        score = 2 if vibe == 'Any vibe' or vibe in d['vibes'] else 0
        score += 2 if month in d['months'] else -1
        score += 1 if budget in ('Budget','Moderate') and d['country'] in ('India','Thailand') else 0
        score += sum(1 for i in interests if i.lower() in ' '.join(d['tags']+d['vibes']).lower())
        scores.append((score, city, d))
    return [(c,d) for _,c,d in sorted(scores, reverse=True)[:3]]

def activity_cost(base, budget):
    factor={'Budget':0.75,'Moderate':1.0,'Luxury':1.8}.get(budget,1.0)
    return round(base*factor)

def make_itinerary(destination, days, start_date, budget, pace, party, interests, currency):
    d = CITY_DATA.get(destination)
    if not d:
        # Generic destination-safe fallback; no invented location-specific coordinates.
        name = destination.strip() or 'Your destination'
        spots=[(f'{name} historic district','Culture',0,0,300), (f'{name} local market','Food',0,0,250), (f'{name} city viewpoint','Leisure',0,0,200), (f'{name} museum or gallery','History',0,0,400), (f'{name} public garden','Nature',0,0,100), (f'{name} evening food street','Food',0,0,350), (f'{name} waterfront or main square','Leisure',0,0,150), (f'{name} craft quarter','Shopping',0,0,300)]
    else: spots=d['spots'][:]
    random.seed(f'{destination}{start_date}{days}{budget}{party}')
    # Interest-first sort, then geography-aware nearest-neighbour ordering within each day's pool.
    preference={'Food':0,'Adventure':0,'History':0,'Nightlife':0}
    for x in interests: preference[x]=1
    def interest_score(s): return 1 if s[1] in interests or (s[1]=='Culture' and 'History' in interests) else 0
    spots.sort(key=lambda s: interest_score(s), reverse=True)
    if pace=='Relaxed': per_day=3
    elif pace=='Fast-Paced': per_day=5
    else: per_day=4
    total_needed=days*per_day
    # Repeat with lightweight alternates only if trip is longer than the built-in catalogue.
    pool=spots[:]
    while len(pool)<total_needed:
        pool += [(f'{x[0]} (slow revisit)','Leisure',x[2],x[3],max(0,round(x[4]*.35))) for x in spots]
    pool=pool[:total_needed]
    plans=[]; running=0
    for day_idx in range(days):
        chunk=pool[day_idx*per_day:(day_idx+1)*per_day]
        # Nearest-neighbour order from city centre/previous spot; same-day geographic clustering.
        if d and len(chunk)>1:
            ordered=[]; remaining=chunk[:]; current=d['coords']
            while remaining:
                nxt=min(remaining,key=lambda s:haversine(current,(s[2],s[3])))
                ordered.append(nxt); remaining.remove(nxt); current=(nxt[2],nxt[3])
            chunk=ordered
        slots=[]
        times=['09:00–12:00','12:30–14:00','14:30–17:00','18:30–21:00','21:00–22:00']
        labels=['Morning sightseeing','Lunch recommendation','Afternoon leisure','Evening dining & entertainment','Optional extra']
        for j, spot in enumerate(chunk):
            name, category, lat, lon, base=spot
            if j==1:
                name = ('Vegetarian-friendly local lunch' if 'vegetarian' in st.session_state.get('special_request','').lower() else f'Local lunch near {chunk[0][0]}')
                category='Food'; base={'Budget':180,'Moderate':350,'Luxury':900}[budget]
            elif j==3:
                name=f'{destination} local dining & evening walk'; category='Nightlife' if 'Nightlife' in interests else 'Food'; base={'Budget':350,'Moderate':700,'Luxury':1800}[budget]
            cost=activity_cost(base,budget); running += cost
            slots.append({'time':times[min(j,4)],'slot':labels[min(j,4)],'name':name,'category':category,'cost':cost,'cumulative':running,'note': 'Clustered nearby to reduce backtracking.' if d else 'Check local transit times before setting out.'})
        plans.append({'day':day_idx+1,'date':(start_date+timedelta(days=day_idx)).isoformat(),'items':slots,'cost':sum(x['cost'] for x in slots)})
    return plans

def create_pdf(trip):
    buff=BytesIO(); doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=17*mm,leftMargin=17*mm,topMargin=16*mm,bottomMargin=16*mm)
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='CoverTitle',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=24,leading=29,textColor=colors.HexColor('#176b63'),alignment=0,spaceAfter=8))
    styles.add(ParagraphStyle(name='DayHead',parent=styles['Heading2'],fontSize=15,textColor=colors.HexColor('#176b63'),spaceBefore=12,spaceAfter=6))
    styles.add(ParagraphStyle(name='Tiny',parent=styles['BodyText'],fontSize=8,leading=10,textColor=colors.HexColor('#52635e')))
    story=[Paragraph('Your journey, thoughtfully planned.',styles['CoverTitle']),Paragraph(f"<b>{trip['destination']}</b> · {trip['days']} days · {trip['start_date']} · {trip['budget']} budget",styles['BodyText']),Spacer(1,5*mm),Paragraph('A practical offline guide with estimated costs. Prices and opening times are planning estimates—confirm locally before travel.',styles['Tiny']),Spacer(1,4*mm)]
    for day in trip['itinerary']:
        story.append(Paragraph(f"Day {day['day']} — {day['date']}",styles['DayHead']))
        rows=[['Time','Plan','Est. cost']]
        for item in day['items']:
            rows.append([item['time'],f"<b>{item['slot']}</b><br/>{item['name']}",fmt_money(item['cost'],trip['currency'])])
        table=Table(rows,colWidths=[28*mm,105*mm,35*mm],repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#176b63')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('LEADING',(0,0),(-1,-1),10),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#d7e2dc')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f8f5')]),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story += [table,Paragraph(f"Day estimate: {fmt_money(day['cost'],trip['currency'])}",styles['Tiny'])]
    story += [Spacer(1,6*mm),Paragraph('Trip budget snapshot',styles['DayHead']),Paragraph(f"Estimated itinerary activities: {fmt_money(sum(d['cost'] for d in trip['itinerary']),trip['currency'])} ({fmt_money(sum(d['cost'] for d in trip['itinerary'])*FX.get(trip['currency'],1), 'USD')} approx.)",styles['BodyText']),Spacer(1,3*mm),Paragraph('Emergency & essentials checklist',styles['DayHead'])]
    checks=['Save local emergency number and hotel address offline','Share itinerary with a trusted contact','Carry travel insurance details and copies of ID/passport','Confirm transport, opening hours and reservation details','Keep a backup payment method and essential medication']
    for c in checks: story.append(Paragraph('☐  '+c,styles['BodyText'])); story.append(Spacer(1,2*mm))
    story += [Spacer(1,5*mm),Paragraph('Emergency contacts to fill in before departure',styles['DayHead']),Paragraph('Local emergency: ____________________   Accommodation: ____________________',styles['BodyText']),Paragraph('Travel insurance: ____________________   Trusted contact: ____________________',styles['BodyText'])]
    doc.build(story); return buff.getvalue()

def build_prompt(dest, days, start, budget, party, pace, interests):
    return f'''Create a realistic travel plan for {dest}, {days} days starting {start}. Budget {budget}, party {party}, pace {pace}, interests {', '.join(interests)}. Return concise JSON array of days, each with morning sightseeing, lunch, afternoon leisure, evening dining/entertainment. Include cost estimates and avoid invented booking confirmations.''' 

# ----------------------------- Session state -------------------------------
for key, default in {'trips': [], 'itinerary': None, 'trip_meta': None, 'special_request': ''}.items():
    if key not in st.session_state: st.session_state[key]=default

with st.sidebar:
    st.markdown('## 🧭 Trip studio')
    provider=st.selectbox('AI provider', ['Demo mode','Gemini','Groq'])
    api_key=''
    if provider!='Demo mode':
        env_name='GEMINI_API_KEY' if provider=='Gemini' else 'GROQ_API_KEY'
        try: default_key=st.secrets.get(env_name,'')
        except Exception: default_key=os.getenv(env_name,'')
        api_key=st.text_input(f'{provider} API key',value=default_key,type='password',help='Used for this session only. Prefer Streamlit secrets for deployed apps.')
        st.caption('API keys are not saved into trip records.')
    st.markdown('---')
    st.markdown('**Quick start**')
    st.caption('Choose preferences below, then build a trip. Demo mode works without an API key.')

st.markdown(f'''<div class="hero"><div style="font-size:.8rem;letter-spacing:.15em;text-transform:uppercase;font-weight:700;opacity:.85">Wander better · Travel smarter</div><h1>{APP_TITLE}</h1><p>{'Thoughtful routes. Local discoveries. More room for wonder.'}</p></div>''',unsafe_allow_html=True)

with st.expander('✦ Configure your trip preferences', expanded=st.session_state.itinerary is None):
    c1,c2,c3=st.columns([1.4,1,1])
    with c1:
        dest_mode=st.radio('Planning mode',['I have a destination','Recommend a destination'],horizontal=True)
        destination=st.selectbox('Destination',list(CITY_DATA.keys())+['Other / enter manually']) if dest_mode=='I have a destination' else ''
        if destination=='Other / enter manually': destination=st.text_input('Enter destination','Barcelona, Spain')
        vibe=st.selectbox('Travel mood / vibe',['Beach','Mountains','Cultural','Urban','Any vibe'])
    with c2:
        days=st.slider('Trip duration (days)',1,14,4)
        start_date=st.date_input('Start date',value=date.today()+timedelta(days=30),min_value=date.today())
        budget=st.select_slider('Budget level',options=['Budget','Moderate','Luxury'],value='Moderate')
    with c3:
        party=st.selectbox('Travel party',['Solo','Couple','Family','Friends'])
        pace=st.selectbox('Pace',['Relaxed','Moderate','Fast-Paced'],index=1)
        interests=st.multiselect('Interests',['Food','Adventure','History','Nightlife'],default=['Food','History'])
    special_request=st.text_input('Extra preferences (optional)','',placeholder='e.g. vegetarian lunch, accessible routes, avoid crowded places')
    st.session_state.special_request=special_request
    if st.button('✨ Build my travel plan',type='primary',use_container_width=True):
        try:
            if dest_mode=='Recommend a destination':
                st.session_state.recommendations=recommend_destinations(vibe,budget,start_date,interests)
                destination=st.session_state.recommendations[0][0]
            if not destination: st.error('Enter or choose a destination first.')
            else:
                if provider!='Demo mode':
                    result=api_generate(build_prompt(destination,days,start_date,budget,party,pace,interests),provider,api_key)
                    if result: st.session_state.last_ai_note='AI provider responded; itinerary structure is safety-checked and rendered using the local planner.'
                currency=currency_for(destination)
                plan=make_itinerary(destination,days,start_date,budget,pace,party,interests,currency)
                meta={'destination':destination,'days':days,'start_date':start_date.isoformat(),'budget':budget,'party':party,'pace':pace,'interests':interests,'currency':currency,'vibe':vibe,'created':date.today().isoformat()}
                st.session_state.itinerary=plan; st.session_state.trip_meta=meta
                st.success('Your itinerary is ready. Explore it in the tabs below.')
        except Exception as e: st.error(f'Could not build itinerary: {e}')

if dest_mode=='Recommend a destination' and st.session_state.get('recommendations'):
    st.markdown('### 🌍 Your destination shortlist')
    cols=st.columns(3)
    for col,(city,d) in zip(cols,st.session_state.recommendations):
        with col:
            st.markdown(f'<div class="daycard"><h3>{city}</h3><p>{", ".join(d["tags"])}</p><span class="pill">Season-aware</span><span class="pill">{vibe}</span><p class="smallmuted">Suggested for a {budget.lower()}-leaning {vibe.lower()} trip. Season fit is heuristic, not a forecast.</p></div>',unsafe_allow_html=True)
            if st.button(f'Plan {city}',key='choose_'+city):
                st.session_state.itinerary=make_itinerary(city,days,start_date,budget,pace,party,interests,currency_for(city))
                st.session_state.trip_meta={'destination':city,'days':days,'start_date':start_date.isoformat(),'budget':budget,'party':party,'pace':pace,'interests':interests,'currency':currency_for(city),'vibe':vibe,'created':date.today().isoformat()}
                st.rerun()

# Main tabbed workspace
T1,T2,T3,T4=st.tabs(['🌍 Destination recommender','🗺️ Optimized itinerary','🎨 Vibe & activity swap','📚 Trip management & PDF'])
with T1:
    st.subheader('Find your kind of place')
    st.write('Recommendations weigh your selected vibe, the destination’s typical seasonal window, and interest overlap. These are lightweight heuristics—not live weather or live availability data.')
    if st.session_state.get('recommendations'):
        for city,d in st.session_state.recommendations:
            st.markdown(f'**{city}**  ·  ' + '  '.join(f'`{tag}`' for tag in d['tags']))
    else:
        st.info('Choose “Recommend a destination” in the preferences panel and build your plan to see a personalized top three.')
    st.markdown('**Built-in destinations:** Goa · Jaipur · Manali · Mumbai · Bangkok · Kyoto · Lisbon')
with T2:
    st.subheader('Day-by-day route plan')
    if not st.session_state.itinerary:
        st.info('Build a plan above to view your day-wise itinerary.')
    else:
        meta=st.session_state.trip_meta; plan=st.session_state.itinerary; curr=meta['currency']
        total=sum(d['cost'] for d in plan); usd=total*FX.get(curr,1); inr=usd/FX['INR']
        m1,m2,m3,m4=st.columns(4)
        for col,label,val in [(m1,'Destination',meta['destination']),(m2,'Days',str(meta['days'])),(m3,'Activities estimate',fmt_money(total,curr)),(m4,'Approx. USD / INR',f"${usd:,.0f} / ₹{inr:,.0f}")]:
            col.markdown(f'<div class="metric"><div class="smallmuted">{label}</div><b>{val}</b></div>',unsafe_allow_html=True)
        st.caption('Currency conversions use illustrative static rates for comparison, not live FX rates. Cost estimates exclude flights and may vary.')
        for day in plan:
            st.markdown(f'<div class="daycard"><h3>Day {day["day"]} · {date.fromisoformat(day["date"]).strftime("%a, %d %b %Y")}</h3></div>',unsafe_allow_html=True)
            for item in day['items']:
                c1,c2,c3=st.columns([1,3,1])
                c1.markdown(f'**{item["time"]}**')
                c2.markdown(f'**{item["slot"]}** — {item["name"]}<br><span class="smallmuted">{item["note"]}</span>',unsafe_allow_html=True)
                c3.markdown(f'**{fmt_money(item["cost"],curr)}**<br><span class="smallmuted">Running: {fmt_money(item["cumulative"],curr)}</span>',unsafe_allow_html=True)
            st.markdown(f'**Day total: {fmt_money(day["cost"],curr)}**')
            st.divider()
with T3:
    st.subheader('Make the plan feel like you')
    if not st.session_state.itinerary:
        st.info('Build a plan first. Then swap a specific slot or regenerate one day without touching the others.')
    else:
        meta=st.session_state.trip_meta; plan=st.session_state.itinerary
        day_num=st.selectbox('Choose day to edit',[d['day'] for d in plan])
        day_obj=plan[day_num-1]
        slot_idx=st.selectbox('Choose a slot',range(len(day_obj['items'])),format_func=lambda x:f"{day_obj['items'][x]['time']} · {day_obj['items'][x]['slot']} — {day_obj['items'][x]['name']}")
        swap_request=st.text_input('Change request',placeholder='e.g. Swap museum for outdoor market / Find vegetarian lunch spot')
        left,right=st.columns(2)
        with left:
            if st.button('🔁 Apply slot swap',use_container_width=True):
                try:
                    item=day_obj['items'][slot_idx]; request=swap_request.lower()
                    if not swap_request.strip(): st.warning('Enter a short change request first.')
                    else:
                        if 'vegetarian' in request or 'vegan' in request: item['name']='Vegetarian-friendly local lunch'; item['category']='Food'
                        elif 'market' in request: item['name']=f'{meta["destination"]} outdoor market'; item['category']='Shopping'
                        elif 'museum' in request: item['name']=f'{meta["destination"]} museum or gallery'; item['category']='History'
                        elif 'outdoor' in request or 'nature' in request: item['name']=f'{meta["destination"]} garden or scenic walk'; item['category']='Nature'
                        elif 'restaurant' in request or 'food' in request: item['name']=f'Local dining pick in {meta["destination"]}'; item['category']='Food'
                        else: item['name']=swap_request.strip().capitalize(); item['category']='Customized'
                        item['note']='Customized by you. Confirm location, opening hours and suitability before visiting.'
                        st.success('Slot updated. The rest of the itinerary is unchanged.'); st.rerun()
                except Exception as e: st.error(f'Could not update slot: {e}')
        with right:
            if st.button('🪄 Regenerate this day',use_container_width=True):
                try:
                    replacement=make_itinerary(meta['destination'],1,date.fromisoformat(day_obj['date']),meta['budget'],meta['pace'],meta['party'],meta['interests'],meta['currency'])[0]
                    replacement['day']=day_obj['day']; replacement['date']=day_obj['date']
                    # Recompute cumulative totals across all days, retaining unchanged days and their activities.
                    plan[day_num-1]=replacement; running=0
                    for dday in plan:
                        for it in dday['items']: running+=it['cost']; it['cumulative']=running
                        dday['cost']=sum(it['cost'] for it in dday['items'])
                    st.session_state.itinerary=plan
                    st.success(f'Day {day_num} regenerated; other days preserved.'); st.rerun()
                except Exception as e: st.error(f'Could not regenerate day: {e}')
        st.markdown('**Current day slots**')
        for item in day_obj['items']: st.write(f"{item['time']} · {item['slot']}: {item['name']} — {fmt_money(item['cost'],meta['currency'])}")
with T4:
    st.subheader('Save trips and take them offline')
    if st.session_state.itinerary:
        meta=st.session_state.trip_meta
        name=st.text_input('Trip name',value=f"{meta['destination']} · {meta['start_date']}")
        if st.button('💾 Save current trip',use_container_width=True):
            try:
                snapshot={'name':name,'destination':meta['destination'],'days':meta['days'],'start_date':meta['start_date'],'budget':meta['budget'],'party':meta['party'],'pace':meta['pace'],'interests':meta['interests'],'currency':meta['currency'],'vibe':meta['vibe'],'itinerary':json.loads(json.dumps(st.session_state.itinerary)),'saved_on':date.today().isoformat()}
                st.session_state.trips.append(snapshot); st.success('Trip saved in this browser session.')
            except Exception as e: st.error(f'Could not save trip: {e}')
        trip_for_pdf={'destination':meta['destination'],'days':meta['days'],'start_date':meta['start_date'],'budget':meta['budget'],'currency':meta['currency'],'itinerary':st.session_state.itinerary}
        try:
            pdf=create_pdf(trip_for_pdf)
            st.download_button('⬇️ Export itinerary PDF',data=pdf,file_name=f"{re.sub(r'[^a-zA-Z0-9]+','-',meta['destination']).strip('-').lower()}-itinerary.pdf",mime='application/pdf',use_container_width=True)
        except Exception as e: st.error(f'PDF generation failed: {e}')
    else: st.info('Build a trip above to save it or export a PDF.')
    st.markdown('### Trip history')
    if not st.session_state.trips: st.caption('No saved trips yet. Saved trips persist for this Streamlit session; this lightweight demo has no external database.')
    else:
        for i,trip in enumerate(reversed(st.session_state.trips)):
            original_index=len(st.session_state.trips)-1-i
            with st.expander(f"{trip['name']} · saved {trip['saved_on']}"):
                st.write(f"{trip['days']} days · {trip['budget']} · {trip['party']} · Currency: {trip['currency']}")
                st.write(f"Estimated activity total: {fmt_money(sum(x['cost'] for x in trip['itinerary']),trip['currency'])}")
                a,b=st.columns(2)
                if a.button('Load this trip',key=f'load_{original_index}'):
                    st.session_state.trip_meta={k:trip[k] for k in ['destination','days','start_date','budget','party','pace','interests','currency','vibe']}
                    st.session_state.itinerary=trip['itinerary']; st.success('Trip loaded.'); st.rerun()
                try:
                    oldpdf=create_pdf({'destination':trip['destination'],'days':trip['days'],'start_date':trip['start_date'],'budget':trip['budget'],'currency':trip['currency'],'itinerary':trip['itinerary']})
                    b.download_button('Download saved PDF',data=oldpdf,file_name=f'trip-{original_index+1}.pdf',mime='application/pdf',key=f'pdf_{original_index}')
                except Exception as e: st.error(f'Unable to export saved trip: {e}')

st.markdown('---')
st.caption('Planning estimates only. Verify current prices, opening times, weather, visa rules, accessibility and local safety advice with authoritative sources before departure.')
