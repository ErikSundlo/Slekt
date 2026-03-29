#!/usr/bin/env python3
"""
Adds English translations and language switcher to the Slekt archive.
Run from the Slekt/ directory: python add_english.py
"""
import os, re

# ── Shared CSS injected into every Norwegian page ───────────────────────────
LANG_CSS = """\
    .lang-switcher { display:flex; align-items:center; gap:4px; margin-right:14px; font-size:0.82rem; font-weight:700; letter-spacing:0.5px; }
    .lang-cur  { color:rgba(255,255,255,0.40); cursor:default; }
    .lang-opt  { color:rgba(255,255,255,0.88); border:1px solid rgba(255,255,255,0.35); padding:2px 7px; border-radius:4px; transition:background 0.15s; }
    .lang-opt:hover { background:rgba(255,255,255,0.15); text-decoration:none !important; color:#fff; }
    .lang-sep  { color:rgba(255,255,255,0.28); }
    .nav-about { margin-left:auto; opacity:0.75; }
    .nav-about:hover { opacity:1; }
"""

def add_lang_to_no_file(path, en_filename):
    """Inject lang-switcher CSS + About into a Norwegian content page."""
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'lang-switcher' in html:
        return  # already done
    html = html.replace('    </style>\n</head>', LANG_CSS + '    </style>\n</head>', 1)
    old = ('        <div class="nav-inner">\n'
           '            <a href="../index.html" class="nav-home">Historisk arkiv</a>\n'
           '            <span class="nav-sep">›</span>\n'
           '            <a href="../index.html">Tilbake til oversikten</a>\n'
           '        </div>')
    new = (f'        <div class="nav-inner">\n'
           f'            <div class="lang-switcher">\n'
           f'                <span class="lang-cur">NO</span>\n'
           f'                <span class="lang-sep">|</span>\n'
           f'                <a href="en/{en_filename}" class="lang-opt">EN</a>\n'
           f'            </div>\n'
           f'            <a href="../index.html" class="nav-home">Historisk arkiv</a>\n'
           f'            <span class="nav-sep">›</span>\n'
           f'            <a href="../index.html">Tilbake til oversikten</a>\n'
           f'            <a href="../about.html" class="nav-about">Om arkivet</a>\n'
           f'        </div>')
    html = html.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

# ── English page template ────────────────────────────────────────────────────
def en_page(title, header, content, no_filename):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} – Historical Archive</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
    :root{{--navy:#1c3557;--navy-light:#2a4a7a;--gold:#9a6e1a;--gold-light:#f5edda;--cream:#faf7f2;--paper:#ffffff;--text:#2d2929;--text-muted:#7a726b;--border:#ddd5c8;--shadow:rgba(28,53,87,0.12);}}
    body{{font-family:'Source Sans 3',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.85;font-size:17px;min-height:100vh;}}
    a{{color:var(--navy);text-decoration:none;}} a:hover{{color:var(--gold);text-decoration:underline;}}
    nav.top-nav{{background:var(--navy);padding:12px 30px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.2);}}
    nav.top-nav a{{color:rgba(255,255,255,0.88);font-size:0.88rem;font-weight:600;letter-spacing:0.3px;transition:color 0.15s;}}
    nav.top-nav a:hover{{color:#fff;text-decoration:none;}}
    nav.top-nav .nav-inner{{max-width:860px;margin:0 auto;display:flex;align-items:center;gap:8px;}}
    nav.top-nav .nav-home{{opacity:0.7;font-size:0.82rem;}}
    nav.top-nav .nav-sep{{color:rgba(255,255,255,0.35);}}
    .lang-switcher{{display:flex;align-items:center;gap:4px;margin-right:14px;font-size:0.82rem;font-weight:700;letter-spacing:0.5px;}}
    .lang-cur{{color:rgba(255,255,255,0.40);cursor:default;}}
    .lang-opt{{color:rgba(255,255,255,0.88);border:1px solid rgba(255,255,255,0.35);padding:2px 7px;border-radius:4px;transition:background 0.15s;}}
    .lang-opt:hover{{background:rgba(255,255,255,0.15);text-decoration:none!important;color:#fff;}}
    .lang-sep{{color:rgba(255,255,255,0.28);}}
    .nav-about{{margin-left:auto;opacity:0.75;}} .nav-about:hover{{opacity:1;}}
    .page-header{{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);color:white;padding:55px 30px 50px;text-align:center;border-bottom:4px solid var(--gold);}}
    .page-header h1{{font-family:'Lora',Georgia,serif;font-size:2.1rem;font-weight:600;line-height:1.3;max-width:760px;margin:0 auto;}}
    .content-wrapper{{max-width:800px;margin:0 auto;padding:50px 30px 80px;background:var(--paper);box-shadow:0 0 40px var(--shadow);min-height:60vh;}}
    .content-wrapper p{{margin-bottom:1.15em;text-align:justify;hyphens:auto;}}
    .content-wrapper p:last-child{{margin-bottom:0;}}
    .content-wrapper h1,.content-wrapper h2,.content-wrapper h3{{font-family:'Lora',Georgia,serif;color:var(--navy);margin-top:2em;margin-bottom:0.7em;line-height:1.3;}}
    .content-wrapper h1{{font-size:1.65rem;font-weight:600;}}
    .content-wrapper h2{{font-size:1.35rem;font-weight:600;}}
    .content-wrapper h3{{font-size:1.1rem;font-weight:600;}}
    .content-wrapper h1:first-child,.content-wrapper h2:first-child{{margin-top:0;}}
    .content-wrapper ol,.content-wrapper ul{{padding-left:1.8em;margin-bottom:1.2em;}}
    .content-wrapper li{{margin-bottom:0.4em;}}
    .content-wrapper blockquote{{border-left:3px solid var(--gold);padding-left:20px;margin:1.5em 0;color:#555;font-style:italic;}}
    footer.page-footer{{text-align:center;padding:28px 30px;background:var(--navy);color:rgba(255,255,255,0.55);font-size:0.82rem;letter-spacing:0.2px;}}
    footer.page-footer a{{color:rgba(255,255,255,0.7);}} footer.page-footer a:hover{{color:#fff;}}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <div class="lang-switcher">
                <a href="../{no_filename}" class="lang-opt">NO</a>
                <span class="lang-sep">|</span>
                <span class="lang-cur">EN</span>
            </div>
            <a href="../../en/index.html" class="nav-home">Historical Archive</a>
            <span class="nav-sep">›</span>
            <a href="../../en/index.html">Back to index</a>
            <a href="../../about.html" class="nav-about">About</a>
        </div>
    </nav>
    <header class="page-header">
        <h1>{header}</h1>
    </header>
    <main class="content-wrapper">
{content}
    </main>
    <footer class="page-footer">
        Historical Archive – The Sundlo and Ringset Families &nbsp;|&nbsp;
        <a href="../../en/index.html">Back to index</a>
    </footer>
</body>
</html>"""

# ── Translations: (english_title, english_header, english_content) ───────────
T = {}

T['Formål.html'] = (
    'Purpose – Introduction by Harald Sundlo',
    'Purpose – Introduction by Harald Sundlo',
    """\
<h1 id="the-world-war-1939-1945">The World War 1939–1945</h1>
<p>Norwegian Volunteers in Russia</p>
<p>Upon retiring in 1992 — a circumstance one greeted with somewhat more relief than one's former colleagues might have wished — I undertook to transcribe a selection of my father's notes concerning our family history, and gathered additionally some new information about the Sundlo and Speilberg families. This material I duly copied and distributed amongst close family members, so that all might know a little more about their origins.</p>
<p>My father had also kept extensive notes from his time amongst Norwegian war volunteers in Russia — the front fighters — and these seemed to deserve a rather wider audience than the immediate family, touching as they do upon matters of some historical interest. I have therefore transcribed a selection of these notes as well.</p>
<h1 id="asker-1993-94">Asker, 1993/94</h1>
<p>Harald Sundlo</p>""")

T['hist3.html'] = (
    'Jørgen Pederssøn Schjelderup',
    'Jørgen Pederssøn Schjelderup',
    """\
<h1 id="jorgen-pedersson-schjelderup">Jørgen Pederssøn Schjelderup</h1>
<p>The Reverend Jørgen was not, as it transpired, destined to end his days in Skogn. In 1656, one Raphael Lund — a theological candidate possessed of the considerable advantage of being nephew to the lord lieutenant Peder Wibe himself — arrived in Trondheim in search of a benefice. It was duly arranged that the Reverend Jørgen should vacate Skogn in Raphael's favour; the latter was called thither on the 2nd of November 1656 and ordained in Trondheim on the 30th of November. The Reverend Jørgen received in exchange the resident chaplaincy at the cathedral and was installed there on the 24th of May 1657. The expectation was, no doubt, that he should in due course succeed his brother-in-law, the Reverend Mentz Darre, who was beginning to show his years. As fortune — or rather misfortune — would have it, the Reverend Jørgen was no more long-lived than the Reverend Mentz. Both incumbent and chaplain died in December 1657.</p>
<p>He had been the first incumbent in Skogn to occupy himself with accumulating landed property. He also took up saw-milling, being the first to build mills deep in the valley, at Kolberg and Reistad. This latter detail suggests that the incumbent had a share in a net fishery in the Beistad fjord, in all likelihood in partnership with his fellow clergy of Innherad.</p>""")

T['hist10 Konrad Bertram Holm Sundlo.html'] = (
    'Konrad Bertram Holm Sundlo',
    'Konrad Bertram Holm Sundlo',
    '<pre> Konrad Bertram Holm Sundlo</pre>')

T['hist 13 Johan Marius Sundlo.html'] = (
    'Johan Marius Sundlo',
    'Johan Marius Sundlo',
    """\
<p>Johan Marius Sundlo</p>
<p>From the notes of Konrad Bertram Holm Sundlo:</p>
<p>"Born the 9th of December, 1886, at Eg Asylum near Kristiansand. Died the 3rd of February, 1933, in Shanghai. Buried May 1933; his ashes were scattered in the Oslofjord, in line with Asker church and the Steilene lighthouse.</p>
<p>I remember my brother Johan from the time he lay in his little bed at Eg. We came to Christiania, and Johan attended the Cathedral School, concluding with the middle-school examination. He then went to sea — on the barque <em>Krimhild</em> of Kristiansand, owned by Schilbred, if I recall correctly; this would have been around 1904. Johan thereafter sailed the oceans of the world: South Africa, Australia, South America. He loaded timber at the White Sea at Onega and made a voyage into the Baltic as far as Riga.</p>
<p>After some years at sea, Johan returned home and took the mate's examination, then went out again, finding himself in East Asian waters when our father fell ill in the autumn of 1908 — though he did not arrive home in time.</p>
<p>Johan remained at home and completed the master's examination, then shipped as bosun on the Søndenfjeldske Line's <em>Kong Ring</em> running between Oslo and Hamburg, later rising to second mate. In the summer of 1913 he took a berth as mate on a Norwegian vessel in East Asia. He sailed in her for a time, but found it not altogether to his taste, and transferred to one of the Standard Oil tankers engaged in the Yangtze trade. He remained in that trade for a while before joining China's largest shipping company, China Merchants Steam Navigation Co., headquartered in Shanghai. He served with that company for many years, and his position had become thoroughly established when, in his mid-thirties, he was given the company's newest and finest vessel to command.</p>
<p>Johan then suffered a misfortune: he contracted an eye condition known as <em>Vogelwing</em> — a membrane growing over the eye — and when treated for it in Shanghai, the eye was so badly damaged that he was obliged to relinquish his command.</p>
<p>He was subsequently appointed to Hankow, in a post roughly equivalent to what we should call a shipping agent, overseeing the company's operations in that city of millions, where he lived for many years. In 1923 he came home on a visit and stood as godfather at Anna Margrethe's baptism in Leinstrand church. Later that summer he returned to China.</p>
<p>He longed, however, to come home to Norway, and in 1932 resolved to do so. He gave notice and departed from Hankow, but when he passed through Shanghai, the company persuaded him to stay and take up a position there — something in the nature of a wharfinger.</p>
<p>One day, whilst clambering about on a roof, he very nearly fell. He caught himself with his right hand, and the jerk was so violent that the upper arm snapped. It transpired that the bone had been hollowed out from within, and that Johan was afflicted with a disease of the utmost rarity. The arm had to be amputated, and his telegram announcing this news read simply: <em>Crippled.</em> Complications then set in; a tumour developed in the chest — cancer, presumably — and on the 3rd of February, his mother's birthday, he died."</p>""")

T['1.Politi.html'] = (
    '1st Police Company – Ensign Bødtker\'s Account',
    '1st Police Company – Ensign Bødtker\'s Account',
    """\
<p>1st Police Company – The Norwegian Legion</p>
<p>As recounted by Ensign Bødtker.</p>
<h2 id="the-hedgehog-position">The Hedgehog Position</h2>
<p>It was on the 4th of December, 1942, that the Russians broke through near Leningrad and drove back the Dutch, leaving the 1st Police Company quite alone in what one can only call a 'hedgehog position' — an arrangement that soon came to resemble an island surrounded by a rising sea. The Russians were pressing in from every direction.</p>
<p>There was snow and poor visibility. One could not determine whether the shadows moving about were Russians or Dutchmen; but as a precautionary measure, one fired upon them all alike.</p>
<p>The Legion lay further to the rear as the Germans' sole reserve and was committed to a counter-attack. At this time it mustered approximately 300 men. The Legion advanced, restored the front, and lost 25 men. The Russians, for their part, had left 700 dead upon the field.</p>
<h2 id="the-ear-that-was-bitten-off">The Ear That Was Bitten Off</h2>
<p>We were faced with Kirghiz troops — disagreeable fellows with long moustaches and prominent cheekbones.</p>
<p>One morning, one of our men, Sergeant Alfred Olsen from Bergen, stepped out of the bunker and found a pistol thrust into his stomach. Not yet entirely awake, and apparently possessed of more sang-froid than good sense, he took it for a comrade playing a prank and knocked the pistol aside with a breezy: "Oh, do give it a rest!"</p>
<p>The Russians who had descended into the trench found no opportunity to withdraw. They were all shot.</p>
<p>On another occasion, some Russians — Kirghiz again — had crawled right up to the edge of the trench, and when the sentry below passed by, threw a tent canvas over him to forestall any inconvenient resistance. One gathers they intended to take him alive, as they had thoughtfully brought along a small sledge.</p>
<p>The sentry, however, made rather vigorous objection to this scheme, fighting back with considerable energy against the gang that had set upon him. The Kirghiz employed knives and teeth alike, leaving the man with a great number of cuts to his chest and throat. One of the Kirghiz had, moreover, bitten off most of one of his ears — and in what remained, one could clearly see the marks of the fellow's rather formidable horse-teeth.</p>
<p>The noise brought other Norwegians running.</p>
<p>"What on earth is going on?" they shouted.</p>
<p>"Shoot, for God's sake!" roared the man, flinging himself flat. Whereupon the attackers took to their heels — those, at any rate, who were still in a condition to do so.</p>""")

T['2 Politi.html'] = (
    '2nd Police Company – The Battle at Chapkosero, 7 March 1944',
    '2nd Police Company – The Battle at Chapkosero',
    """\
<p>2nd Police Company – The Battle at Chapkosero, 7th March 1944</p>
<h1 id="rolf-orenes-account">Rolf Orenes's Account</h1>
<p>After the New Year of 1944 things had grown increasingly unsettled on the Kandalaksha front, where the Russians were making preparations for the great offensive that would, among other things, destroy the Norwegian Ski Battalion. Across the whole sector, Russian forces were advancing with reconnaissance units of up to battalion strength; and it was one such battalion that on the 7th of March 1944 struck the 2nd Norwegian Police Company, then stationed at Chapkosero as the furthest-forward outpost to the east.</p>
<p>The company, under the command of Company Commander Beck, comprised four platoons, each of four sections — sixteen sections in all, every one equipped with a light machine gun. Normal section strength was ten men, though not all sections were at full establishment.</p>
<p>The company had disposed itself in two strongpoints, with half the company at each. Commander Beck had command of one strongpoint, situated on a sort of islet surrounded by water or bog — though at this season everything was covered in snow and frozen solid. A fringe of woodland immediately surrounding the position provided concealment but simultaneously impeded the view outward. Beyond this belt of trees, the ground lay open for several hundred metres before the forest resumed.</p>
<p>The garrison of the strongpoint numbered 72 men. The other half of the company had established themselves in a second strongpoint some two kilometres distant.</p>
<p>The company was the sole Norwegian unit on this section of the front, the units to its right and left being German. It had arrived on the Kandalaksha front in February 1943 and remained there until May 1944.</p>
<p>Russian activity had not gone unremarked, and when on the 7th of March they advanced with a reinforced battalion — some 600 men — they found the Norwegians at the highest state of readiness.</p>
<p>Beck's 72 men had arranged themselves with one timber bunker per section, so positioned that the bunkers mutually supported one another. The whole was ringed with barbed wire, and each section had posted a sentry.</p>
<p>The weather was clear and cold.</p>
<p>The Russian battalion sent patrols ahead, and owing to the woodland and the darkness these succeeded in reaching the wire and cutting through it undetected. Only when the Russians were already inside did the sentries become aware of them and fire the alarm. The time was 04.30.</p>
<p>On the company's right flank lay the bunker of 1st Section, 1st Platoon, with Section Commander Kåre Berg and Rolf Orenes as first machine-gunner. Roused by the shooting, the entire section came storming out and took up position — but by then the Russians were barely five or six metres away.</p>
<p>Orenes threw the machine gun into position, but could not make the automatic mechanism function: it had frozen solid. "Confounded cold!" He therefore dropped the machine gun and fell to throwing hand grenades, whilst the section's two riflemen — one on each side of him — began picking off Russians with aimed fire. This proved insufficient against the mass that was pressing in. Matters looked decidedly grim, and grew grimmer still when the Russians brought forward a flame-thrower and swept it back and forth across the position.</p>
<p>"We were frightened," said Orenes — "simply frightened. We withdrew four or five metres behind the bunker for protection from the flames, and shouted for help at the tops of our voices."</p>
<p>Help arrived — a mere seven men, but they were seasoned soldiers who knew no hesitation, and their leader, Under-Section Commander Johan Gundersen of Grimstad, was not a man given to prolonged deliberation. With a roar, this powerfully built individual charged forward at the head of his men; simultaneously the company commander came running up. Seeing his first machine-gunner standing there throwing grenades, he shouted: "Why aren't you shooting?" — "It won't work! It's too cold!" Orenes replied.</p>
<p>Beck then seized the machine gun himself and fired from the hip — but obtained only single shots. The automatic mechanism would not function.</p>
<p>Meanwhile grenades flew from both sides, as the Russians were similarly equipped. One grenade found Company Commander Beck, tearing open his entire right side. Beck fell, but his last ringing order was: "Don't let the swine take you!"</p>
<p>A furious battle ensued; the Norwegians pressed forward to avenge their fallen commander and drive out the Russians. The reserve that had come up carried half a case of grenades, but these were soon exhausted. The grenades flew thick as hail against the Russians; then Gundersen leapt up and charged, followed by all the others, with Orenes at his side.</p>
<p>Two Russians had got inside the bunker and were doing their best, though not for long. With a sub-machine gun held by the barrel, Gundersen stove in the skull of one; the other suddenly found himself in Orenes's grip, who had gained the upper hand and was pressing the man's arms to his sides. A furious wrestling match ensued to the accompaniment of exploding grenades — back and forth they strained until the Russian's arms went slack, whereupon Orenes flung him away with a vigorous shove, drew his bayonet, and thrust — and that particular Russian would not be troubling any more Norwegians.</p>
<p>"It was dreadful," Orenes reflected. "But it was him or me."</p>
<p>The other Norwegians had meanwhile dealt with those Russians who had climbed onto the bunker roof, and the strongpoint was once again entirely in the company's hands. With this effort the section had broken the back of the Russian attack — fortunately, since they had only one man wounded. But their Company Commander Beck was dead.</p>
<p>From the two fallen Russians inside the bunker, the Norwegians took two sub-machine guns — a considerable reinforcement — and these worked perfectly. They blazed away!</p>
<p>The Russians now withdrew, and with some urgency when a Norwegian flanking post with a heavy machine gun opened up, sweeping the ground all the way to the wire.</p>
<p>After a comparatively quiet interval of about half an hour, the next attack came in. Four Germans who had remained in the strongpoint had set up a 3.5 cm mortar — the Norwegians had none such — and with this mortar and their own weapons the garrison beat back three separate Russian attacks that morning. Each time the Russians committed roughly 300 men, advancing in the characteristic Russian 'surprise formation' — packed together like a wall of flesh, with no preparatory fire.</p>
<p>"Damnably easy to repel such an attack, when one has decent weapons."</p>
<p>The attacking troops were Russian élite — the very units employed in the great offensive to follow.</p>
<p>When the attacks had been driven off, the Norwegians had three grenades left and one case of ammunition. Had the Russians attempted one more assault, they would have broken through.</p>
<p>At around noon, when the Norwegians went out to examine what lay in the field, 20 Russians came towards them with their hands raised and surrendered. Several were severely wounded.</p>
<p>Some of the wounded Russians then suddenly opened fire on the Norwegians — "and we had no choice but to throw ourselves down and shoot accurately, until all the Russians were dead."</p>
<p>"When we had finished, we found we were damnably hungry, and accordingly began rummaging through the Russian packs and the stores they had brought forward on reindeer-sleds. We were fortunate. The Russians were liberally supplied with such agreeable things as American chocolate, and so we held a sort of gala dinner on the spot."</p>
<p>"We had telegraphed for reinforcements, and when we saw a unit of about 40 men in white camouflage approaching, we took them for our own and waved. They waved back. But suddenly they deployed in line and opened fire. We threw ourselves down and returned fire."</p>
<p>Some of the Norwegians attempted to outflank the Russians and take them in the rear; in this action the German Burgdorf was killed. A couple of Russians managed to escape. In all, the Russians lost 126 dead and 26 prisoners, whilst the strongpoint's garrison lost two men killed and one slightly wounded.</p>
<p>Johan Gundersen was recommended for the Iron Cross First Class. He never received it. It was awarded instead to the German who had taken command when Company Commander Beck fell.</p>
<p>Matters then quietened somewhat; in April the company was relieved by the Ski Battalion, which would find itself on the receiving end of the great Russian offensive that subsequently destroyed it. The battalion lay, as Norwegians invariably did, furthest forward to the east.</p>""")

T['3politi.html'] = (
    '3rd Police Company – Company Commander Berg',
    '3rd Police Company – Company Commander Berg',
    """\
<p>3rd Police Company — Company Commander Berg</p>
<p>(As recounted by Leif Stensønes)</p>
<p>Stensønes was deputy section commander in 4th Section, 3rd Platoon, and accordingly armed with a sub-machine gun.</p>
<p>The company came to Germany in June 1944 and from there proceeded to Finland, arriving a few days before the Ski Battalion was destroyed — thus around the middle of August.</p>
<p>The company lay first in Oulu for eight to fourteen days, and then continued by rail to Rovaniemi–Kemijärvi to relieve the Ski Battalion, though it arrived too late for that purpose.</p>
<p>Having passed Kemijärvi, the company halted to rest at a German billet. During the night the billet was bombed from the air, and Stensønes received a shell splinter in his left cheek. He lost consciousness and did not come to himself again until he was in hospital in Oulu, where he lay for fourteen days.</p>
<p>Upon his discharge, when he was to return to the company, Finland capitulated.</p>
<p>The 3rd Police Company had numbered 200 men on its arrival in Finland, but in Oulu some 60 to 70 were detached to the Ski Battalion.</p>
<p>Stensønes was sent to hospital in Germany, while Captain Berg received orders to lead the 3rd Police Company back to Norway. This came to nothing, however; Captain Rustan took over and led the company on its march from Finland over the mountains to Narvik — a truly remarkable feat of endurance.</p>
<p>In Norway, the company was to have been inserted into the German defensive line in the Lyngen area, facing northward and supported by fortifications out at sea.</p>""")

T['5konordl.html'] = (
    'With 5th Company, Regiment Nordland – Dagfinn Henriksen',
    'With 5th Company, Regiment Nordland – Dagfinn Henriksen',
    """\
<p>With 5th Company, Regiment Nordland</p>
<p>(As recounted by Dagfinn Henriksen)</p>
<p>In January 1941 I volunteered, and was called up in February for examination. Seven doctors: one for the ears, one for the nose, one for the legs, and so on — we were quite thoroughly inspected.</p>
<p>I subsequently reported to Bjølsen School in Oslo, from which I was sent, together with roughly 100 other volunteers, by air to Aalborg in Denmark, thence by train to Munich — where we stopped a couple of days to look about — and then on to Graz.</p>
<p>Initial recruit training took place in Graz with the regiment <em>Der Führer</em>, and lasted until Easter 1941. At Easter we were sent to Heuberg on Lake Constance, where Regiment Nordland was formed up with artillery, flak, and all appurtenances — though no armour.</p>
<p>Divisional commander: Steiner. Regimental commander: von Scholl.</p>
<p>I was assigned to 5th Company, that is to say Battalion II.</p>
<p>We then made for the front — by rail through Nuremberg to Breslau, and thence by lorry to the Lemberg area. We departed Heuberg in early June 1941 and reached the front a couple of days before war broke out. We lay in a tented camp and one morning were woken by the tremendous explosions of <em>Stukas</em> that had commenced bombing the Russians.</p>
<p>We knew there would be war, though not much beyond that. We had been told at Heuberg that we should march through southern Russia and the Caucasus to join up with the Africa Corps in Egypt, and that the Russians were peaceably disposed and would permit such a march. One received this information with the appropriate degree of credulity.</p>
<p>In broad outline, my war went as follows: Heuberg — the frontier — an area some 7 km north of Rostov — back to the River Mius, where I was wounded in the face by a shell splinter — then to Vienna by hospital train on New Year's Eve, and three months in hospital. Replacement battalion in Klagenfurt, then convalescent home in Toppelbad near Graz for six months. Thence to SS-Hauptamt Berlin for a fortnight, and then welfare officer in Oslo. Demobilised February 1943.</p>
<p>Decorations: Iron Cross 2nd Class, wound badge, assault badge, Eastern Front medal, War Merit Cross.</p>
<p>The war began early in the morning — I believe at around five o'clock. The Germans advanced along the entire front; we, however, were not among them. I believe we lay where we were throughout that first day.</p>
<p>The company commander arrived with a map and read out an order forbidding us to drink water, accept food, enter Russian dwellings, or go about alone — a great many such prohibitions, backed by severe penalties for non-compliance. They feared poison in the food and water.</p>
<p>Pioneer and armoured units crossed the border first. When we came across, we found colossal quantities of Russian tanks and vehicles lying burnt out and hideous in long columns. We ourselves had no contact with the enemy until we had passed Lemberg, where we were received with flowers and cigarettes.</p>
<p>I was initially second machine-gunner, later first. I laboured all summer until I was nearly deranged. The first gunner fell at Dniepropetrovsk. Pay was one mark a day, two at the front; and every ten days there was a pay parade, so one had a little to spend at the canteen lorry — for we had no canteen as such, only the lorry, looked after by the <em>Spiess</em> — the senior NCO, the company's 'mother', two bands on his arm.</p>
<p>Rations were often wretchedly poor. I have seen German soldiers take the iron ration from fallen comrades — that is, the emergency provisions — but not trouble to collect their paybooks, which they were duty-bound to do.</p>
<p>On the 7th of July 1941 we came to a town — large, handsome, with fine streets. There I recall the Poles requesting permission to fight alongside us; the Germans would not allow it. They were permitted, however, to round up Jews, and one then witnessed the ferocious hatred the Poles bore towards them. That I should live to see such a thing, and before I had even been in battle. The house we were billeted in lay on the outskirts of the town, near the cemetery. And thither the Poles drove the Jews — young, old, men, women, and children. The wretched people were lined up by open graves and told to remove their shoes.</p>
<p>That was all. They were then shot and tumbled in — or shoved in, when they did not topple in of themselves. The hatred was so absolute that no form of words can adequately characterise it.</p>
<p>Our first engagement with the Russians did not come until after Lemberg. The battalion's real baptism of fire was the fighting for Hill 24, immediately west of Kiev. There came the order: <em>Absitzen! Fertigmachen zum Gefecht!</em> — Dismount! Prepare for action!</p>
<p>The lorries drove back whilst we advanced by bounds. We had been detailed as cover for the other troops pressing forward to take Kiev. We arrived on Sunday the 20th of July at first light and lay there, as best I recall, for about a day before moving off in the night.</p>
<p>The Russians had positioned a fearful quantity of artillery and shelled us throughout the day; they also sent forward great numbers of tanks, which we knocked out. Here Rolf Halmrast from Drammen fell — the first Norwegian amongst us to be killed.</p>
<p>The battalion was deployed with 5th Company on the right and 7th Company on the left; we could see across to each other. Foul weather that day — rain and mud.</p>
<p>The sections lay in small holes, two men to each, and the first thing one did was make them deep enough to provide cover.</p>
<p>Every now and then the cry went up: <em>Panzer vorne!</em> There were many kinds of tanks, some with and some without turrets. One turret was shot off, but the tank continued to roll forward. Six or seven of them passed us. We had no anti-tank guns to speak of. The 3.5 cm <em>Pak</em> was useless against the armour. The Russians drove around the hill and wreaked havoc; then German tanks arrived and drove them off.</p>
<p>The Russians were prepared for our arrival and had everything ready. The bombardment they brought down on the hill killed three men. What saved us was that we had advanced into a finished position. In the midst of the shooting I flew across to the next hole to cadge a cigarette for myself and my companion. I risked my life for that cigarette.</p>
<p>On the evening of the 20th of July we were pulled back and relieved by the Wehrmacht. On the 21st the advance on Kiev continued. We came to a village I have forgotten the name of; dismounted, shouldered our packs, and marched eastward towards Kiev. We simply zigzagged around the city for two days without casualties — then were set in motion southward, and some days later came into action near Smela, west of Dniepropetrovsk. I was engaged in clearing some houses — we were burning the entire village, every single house, because they had concealed Russians in them.</p>
<p>We were not seriously committed until the Dnieper. Until then we had been spared. Now we were to screen Guderian's panzer army. Since the Russians lay on our side of the river, a reconnaissance patrol preceded us; but when we arrived we had a pleasant time of it, taking over security along the bank with a couple of hundred metres between each post.</p>
<p>In August 1941 the Wiking division was drawn southward along the Dnieper to Dniepropetrovsk, which lay with its greater part on the western bank. The western bank had been taken by the SS Regiment Germania, also part of the Wiking division — the other regiments being Nordland and Westland.</p>
<p>We reached Dniepropetrovsk early in the morning and found a small pontoon bridge across the river — a few planks, really. Coming under Russian fire, we had to creep along the walls. The bridge was shot to pieces again and again; we crossed it fifty paces apart.</p>
<p>On the far side, hell was even hotter. We lost men freely and dug ourselves into a park. All went tolerably well at first, as the soil was loose near the surface; but then we struck gravel, and hacked at it like madmen with our bayonets. Having dug myself a hole, I lay in it and did not stir until evening.</p>
<p>We then went into billets further out in the suburbs, where I suffered the great shaking. No food, nothing to drink, heat like a furnace, and the shells raining down. And the crack when the Russian tanks fired between the housing blocks — <em>bang!</em> Lord.</p>
<p>Crossing the great railway yard, a shell — certainly a twenty-centimetre — arrived and took the legs off a Finn. The poor wretch lay moaning, and Bjørn Johansen and I dashed out after him. We lifted him between us, but at that very moment a shell arrived and nearly knocked us both down. Our clothes were riddled throughout — trousers and tunic both — and one of my boot-toes had been cut off. But neither of us had a scratch. Quite extraordinary: a whole shower of holes through our clothing.</p>
<p>We dragged the Finn to safety, but he died as we attended to him.</p>
<p>In the evening we had fought our way to a pump, where we drank ourselves full of water — though there was such a crush that we practically came to blows over it. We then went into billets in the long street containing a power station.</p>
<p>Outside Dniepropetrovsk lie vast stretches of sandhills. Sand, sand, and more sand. Here we lost, among others, our first machine-gunner; and many others besides. District Physician Hansen of Holmestrand lost both his sons on the same day — one in the morning, the other at about ten o'clock.</p>
<p>LARSEN, who is listening: "Lord, yes. It was dreadful. The only time I began to feel faint. We fought all day in that sandy desert, but when the Russians once began to run, they ran fast enough! We came upon the Russians rather too quickly. There were several senior Russian officers up in the front line on an inspection visit, and they were killed. We got a dressing-down for it, because we should have tried to take them prisoner."</p>
<p>HENRIKSEN continues: The Russians had no idea we should launch a major attack the day after taking the city. But that is what we did. We fought our way through the entire sandy desert and found ourselves well ahead of the Wehrmacht, so we had to fall back — a weary business. But we did at least find some water in a village and managed to knock some apples from a tree. Then we dug ourselves in for the night.</p>
<p>During this attack, Leif Gunnar Overn of Modum (aged 20) and Arne Mathisen of Drammen went missing. Unable to conceive that the attack would halt, they ran straight on. They ended up ahead of us, in a village full of Russians — but found cover and returned to us during the night.</p>
<p>(Leif Overn's brother Hans tells the story of a front fighter who described just how cool Leif was: during a Russian artillery bombardment, Leif went strolling along, whistling. We heard a shell coming; Leif threw himself flat, the shell burst close beside him, and Leif continued on his way, still whistling the same tune.)</p>
<p>Overn fell subsequently.</p>
<p>HENRIKSEN continues: On the eastern side of the sandhills we lay on a height, with forest below. At about ten or eleven at night I was on forward sentry duty in a hole. It was pitch dark, but I had binoculars, which I used diligently. Suddenly I saw something dark in front of me. It moved, and I heard a clink — which turned out to be a fixed bayonet. A Russian was creeping up on our position.</p>
<p>I was uncertain what to do. But I had the advantage that I, through the glasses, had spotted the Russian while he had not seen me. He came right up to me and started violently when I shouted "Hands up!" twice. I knew no Russian, and in my alarm I sang out in English. The effect, however, was excellent. The Russian was dumbfounded and dropped his rifle.</p>
<p>Leaving my companion in the hole to keep watch, I took the Russian back to the company command post. The commander had a interpreter with him, and extracted from the Russian the information that the Russians intended to attack at one in the morning, driving through the forest to the left of me. The company commander immediately alerted the battalion commander, who made his dispositions — directing artillery and other weapons against the forest.</p>
<p>When the Russians came storming forward with their hurrahs, the battalion commander opened fire and shot the forest to pieces. Good Lord, the screaming and howling from over in the trees! It had been packed with Russians, and was now utterly devastated.</p>
<p>But had we not known of the attack and been ready for it, with our ammunition prepared, it would have gone very badly for us.</p>
<p>The strange thing is that when, the following day, I tried my pistol and my rifle, I could make neither function. Both were choked with sand.</p>
<p>I received the company commander's thanks for a good watch. It is the finest thing I did.</p>
<p>The Wehrmacht had been driven back north of Dniepropetrovsk, and we were sent up through the city to relieve them.</p>
<p>In August 1941 we had our 'textbook attack'. We were supported by Italian artillery using airburst shells. An old woman said that the Russians had taken their artillery back.</p>
<p>First we advanced through a maize field tall enough to afford good cover. But emerging onto a tomato field where we could be seen, we switched to bounds — executed quite splendidly.</p>
<p>We moved forward at great speed, with only one man in each group moving at a time. We went through the field, through the Russian position, and through a village. We found 86 Russian dead in the trenches. My company had only two killed and four wounded; the other companies' losses were similarly light, if not lighter. The regimental commander was lavish in his praise, and the battalion commander walked about as proud as a cock.</p>
<p>That night a Russian air attack came in, and three bombs were dropped. Two fell in open ground; the third fell on a schoolhouse full of Russian prisoners, killing 20 to 30 and wounding 40 to 50. None of our people were hit.</p>
<p>A day or two later we took part in a large advance in attack formation, some 70 km east of Dniepropetrovsk. We marched many, many kilometres through maize and flax fields — the maize being particularly unpleasant, as one had to shove the stiff stalks aside to make progress.</p>
<p>LARSEN: The third gunner had been wounded, so I had to carry an ammunition case in each hand. Wretched work — I couldn't have managed it today.</p>
<p>HENRIKSEN: I went along carrying things in every conceivable posture — now upright, now crouching. The sweat poured in streams.</p>
<p>LARSEN: I had a packet of cigarettes in a pocket and thought I'd have a smoke. But when I got the packet out, it was nothing but a soggy mess of sweat, so I had to throw the whole business away. We had a hard time of it then. We lay out in the open for nights on end.</p>
<p>HENRIKSEN: We pressed forward by day in attack formation, and when one thought one might at last get some rest at night, one was sent on patrol all night instead. Next day, forward again — and then suddenly the shells came raining down, and it was a matter of digging in at speed.</p>
<p>We came one day to a village that turned out to be thickly held, snipers even in the trees. We were peppered abominably and many fell. I was slightly wounded and reached a dressing station that was crammed full and resembled a slaughterhouse. Several other Norwegians were wounded that day — Tvedt and Svendsen among them. How the fight ended, I do not know, as I was on the table by then.</p>
<p>LARSEN: I was lying with Odvar Ness from Rena. He fell later. We lay together behind a haycock when something struck Odvar's helmet. A bullet had passed clean through it — without wounding Odvar.</p>
<p>HENRIKSEN: Have you heard about Aalholm? We had been fighting all day in those sandhills, and in the evening, when Aalholm took off his helmet to breathe, he found a Russian bullet inside it. He had not noticed the helmet being hit.</p>
<p>LARSEN: I very nearly had a mortar round straight in the head! I was sitting with a comrade in a slit trench, and next to it we had dug a small latrine. I was about to get across to it — had one leg up on the parapet and was supporting myself on my hands, ready to swing over — when we suddenly heard the whine of an incoming mortar bomb. My comrade grabbed me and yanked me back into the trench, and the instant I took cover the round struck the ground precisely where my head had just been.</p>
<p>HENRIKSEN: Once when I was lying shooting, a shell burst 15 metres from my head. I was not hit, but my shoulder strap was cut clean through.</p>
<p>HENRIKSEN continues: We did not take the town we had been advancing on. We were relieved.</p>
<p>One ammunition case weighed 12.5 kg. We were entirely exhausted by carrying one about all day — throwing oneself down, getting up again, and so on. But we had one man, Eivind Jonassen of Drammen, who ran about with four cases — though he was, admittedly, in the Legion.</p>
<p>We pressed steadily forward, moving ever further south. One night we received orders to make ready, and the entire division — and more besides — drove flat out in the pitch dark straight through the Russian lines. We went at full tilt, and when we had broken through we occupied all the villages behind the Russian positions. The Russians wandered about in complete bewilderment, encountering German tanks wherever they turned.</p>
<p>We took over 80,000 prisoners. My company lost only two men on a patrol.</p>
<p>(For this action, see Liddell Hart: <em>The Other Side of the Hill.</em>)</p>
<p>I was billeted in a village where 16 Finns had shot down a couple of hundred cavalrymen, and was sent out on patrol immediately. We were two sections. Having gone some distance, we dismounted from the lorry to continue on foot, while a NCO stayed with the driver, who had driven all night and was quite done in. It turned out that both of them fell asleep. We heard shots and returned — only to find two Russian tanks arriving, which opened fire on us without hitting us as we flung ourselves flat. The tanks drove on; we ran after them and, coming up onto a rise, saw that one was towing our lorry.</p>
<p>On a later patrol to another village, I came across the lorry — stripped completely bare. I had lost a watch and a camera.</p>
<p>The NCO we found shot through the head. The German driver had been taken prisoner — so some Russian civilians told us.</p>
<p>We then marched on, approaching Rostov. The division came to a village; our battalion was in the lead, my section as the spearhead. We went through the village and when we neared the political commissar's house — a brick building — we advanced most carefully. Suddenly there was an enormous explosion and the section commander vanished. He had trodden on a mine and been blown to pieces, his remains scattered into the ditch. Taking over command, I went to him and took his paybook and sub-machine gun. While I was doing this, a hellish fire broke out from every direction, and we had no choice but to make our way out to the right across a bog, crawling up a slope to a house that stood there. It was a wretched business — we sank into the bog, the Russians fired, we ran and fell and crawled, and arrived at the house completely spent. We decided to hold there for a time, but prudently sent a man across to the slope by the stream — which was well judged, for he came sprinting back to report the stream bed swarming with Russians.</p>
<p>We made off, through a great cornfield and across to a village. We lost only the section commander; and I received a commendation from the platoon commander for having brought back the section commander's paybook and sub-machine gun.</p>
<p>We advanced north of Rostov, consistently kept away from all towns. I have not a single amusing incident to report from there. Once we were brought forward, we were always at the front.</p>
<p>When we came back into rest billets, it was parade from morning to night — drill and guard duty around the clock. Dreadful. We were glad to get back to the front.</p>
<p>The SS was moved from one place to another without pause — entirely motorised. When things became critical, the SS was called in. Certain Austrian and German mountain troops from the Wehrmacht were an exception; they were fully the equal of the SS.</p>
<p>On the 16th of November, our section was on patrol some 16 km ahead of our village. We had encountered no Russians, but coming to a railway embankment and crawling up it, we saw the other side thick with them.</p>
<p>Some Russians came forward to intercept us. A unit was sent round to outflank us, and a cavalry detachment also set itself in motion. We ran down from the embankment and into a stream bed, which we followed at the double.</p>
<p>The Russians then wheeled in towards us. We took up position and fired at close range with all weapons. The Russians ran; we made off at full speed and arrived, quite spent, at a village unlike any we had previously encountered — cleaner and finer, and the people quite different. They took care of us, served wine and food, and posted sentries to warn of any approach. The village was an oasis.</p>
<p>We bade these people a heartfelt farewell and made our way back to our village.</p>
<p>On the evening of the 18th we were brought up as the battalion's last reserve. We had jackets, shirts, trousers — but no underclothing, all that having gone missing in the village — and no greatcoats.</p>
<p>We set about digging positions in pairs, and this saved us — we were just able to keep warm. It was minus 35 degrees with a biting wind. We lay on the ground and hacked at the earth with our bayonets. By morning my German companion and I had dug a hole for three men.</p>
<p>We had no greatcoats because our lorry had been taken by the Russians.</p>
<p>This was a terrible piece of cold work, and the Germans suffered appalling losses when the Russian offensive developed into the greatest catastrophe of the war for us, spreading across the entire front.</p>
<p>In the morning the Russians attacked us, just as they attacked 7th Company. We were ordered to hold until we received the order to retire, our task being to defend the bridge. The river was not solidly frozen; and there my platoon lay.</p>
<p>Only when the Russians were twenty metres from us did we receive the order to fall back. We fired everything we had. We fired until the platoon commander signalled us to go — then we snatched up our rifles and sprinted across the bridge.</p>
<p>By firing with all our might we had made the Russians fling themselves down before our position. But climbing up from the bridge and onto the high ground, the Russians fired like madmen. Even so, exposed as we were, not one of us was hit.</p>
<p>At the crest we held for a moment, then ran on again. It was continuous retreat; but towards evening we reached a place with a great many fine haycocks. There I found Arne Mathiesen from Drammen. We burrowed into a haycock and fell asleep at once, and did not wake until someone trod on us. A German. Do you know why he trod on us? Because he was German and had the German discipline drilled into him. When he had retreated, he had forgotten the spare barrel for the machine gun behind him, and had accordingly run back — alone — to find it. And he did find it. We then joined forces with him and ran back. But had he not trodden on us, we should have been killed or taken. As it was, I found my unit again — though in those days I had neither eaten, nor slept, nor been under a roof.</p>
<p>Now the entire battalion was assembled in the village where I found it, and we were ordered to make off and manage as best we could.</p>
<p>And make off we did. Some on foot, some on lorries. But the guns were blown up.</p>
<p>Our section had no lorry. 3rd Section got a seat on a Russian Ford.</p>
<p>While looking for a lorry, we had fallen behind, so the driver wanted to push ahead to make up time. But he drove us into a ditch. We took what was most necessary, blew up the rest, and set off on foot. By this time we had come up onto a main road and tried to board the lorries streaming past — but they were all full, so we were left standing quite alone. We ran — ran and walked, ran and walked, until morning, when we reached a village full of all manner of units. We slept a little there, but then came the cry: <em>Die Russen kommen!</em></p>
<p>I slipped into a delivery lorry with a Volksdeutsche from Romania, and we drove to another village, where we were put down. We were billeted after a fashion, but were soon roused again: <em>Die Russen kommen!</em></p>
<p>This went on again and again until we found ourselves at a Wehrmacht field kitchen. Four of us had kept together — a Dane, a Finn, the Volksdeutsche, and I; and at that kitchen we were well treated.</p>
<p>Then one day I ran straight into my damned platoon commander. Naturally I reported back. "Are you mad?" said the platoon commander. "Mad?" said I. "Haven't we got it nicely here?" said he.</p>
<p>So I stayed at the kitchen, peeling potatoes, until a column of vehicles arrived carrying the whole of Wiking. The city commandant told us to stand by the road and jump on when our unit came past. And when 5th Company came along, we jumped on. We had been on our own for a fortnight.</p>
<p>We came to a village where a thorough check was carried out. Of 5th Company, 36 men remained.</p>
<p>LARSEN: Then we met Germania at full strength. But we were a sorry lot. Of the entire battalion, only 90 men remained fit for action; of our platoon, only 12.</p>
<p>During the retreat, one night the road ran straight through the Russian lines, who lay on either side and took us for Russians.</p>
<p>On one occasion we managed to hitch a ride on a German tank.</p>
<p>We ended up finally in a small village just before the front, slaughtered cows and pigs, and lived extremely well whilst performing postal duties. Then we were relieved — and the next day the Russians came like a thunderbolt. Of those who relieved us, not one got away.</p>""")

T['7konordl.html'] = (
    'With 7th Company, Regiment Nordland – Erling Larsen',
    'With 7th Company, Regiment Nordland – Erling Larsen',
    """\
<p>(With 7th Company, Regiment Nordland)</p>
<p>(As recounted by Erling Larsen)</p>
<p>I served in 1st Battalion, 7th Company, Regiment Nordland, and travelled to Germany together with Dagfinn Henriksen, who was assigned to 5th Company. My route was: Heuberg — the German–Russian border at Lemberg — Rostov — 7 km further north — back to the Mius, where I was wounded in December 1941 — Ostenskaya hospital — Iduvànskaya — Lemberg hospital — Klagenfurt convalescent home and transfer to Regiment Westland, 2nd Company. Demobilised June 1942 in Berlin.</p>
<p>Decorations: Iron Cross 2nd Class, wound badge, assault badge (minimum 3 assaults required), Eastern Front medal, War Merit Cross.</p>
<p>Shortly before reaching the Lemberg sector, the men had been issued Russian phrase-books. It had been said that we were to march through Russia — that Russia had given free passage for this transit — and that we might thereby establish contact with the Africa Corps. The Russians were peaceably disposed, one had been told. The war came as a surprise to us all.</p>
<p>On the 21st of June, 1941, I was doing extra guard duty — punishment guard, since my watch commander had had a birthday and we had drunk and celebrated somewhat longer than was prudent, earning me a week's extra guard. I stood watch alone.</p>
<p>Then suddenly in the night came a great many aeroplanes, and from far away came rumble upon rumble of bombs and guns — a distant, rolling thunder. This was at about five in the morning, still dark.</p>
<p>Only the following day were we told: During the night, German troops had crossed the border, and we are to follow. The company commander read out an order and hung up a map of Europe. He pointed — a long sweeping arc: "This is Russia and this small thing here is Germany. It may look rather unpromising; it may be a trifle sobering that we, this small patch, are to conquer all that great Russia — but we shall manage it." One received this assurance with somewhat divided feelings.</p>
<p>The entry into Lemberg was rather like King Haakon VII's return to Oslo in 1945. Wild jubilation amongst the population of Lemberg; swastika flags everywhere; people running forward throwing flowers, cigarettes sailing through the air.</p>
<p>Our first contact with the enemy came south-east of Lemberg, where the company commander and 7 men fell.</p>
<p>We came down a slope where 15 cm artillery stood, moved on down a valley through some large cornfields. In the valley below was a small village, and on the height opposite one could see the Russians with quantities of vehicles and tanks. We found some positions. One of the comrades, Mathias Olsen, said: "Can you see the Russians?" Behind us was a battery of four guns, 20 to 30 metres away. Just as Mathias said those words, the first shot went off. I had turned my head towards him and received the concussion full in the cheek and sat down hard. Then we saw the shells land. We could plainly see our artillery making havoc on the far side — the Russians running about in complete confusion, vehicles bouncing in every direction from the shell bursts. The Russians had no time to return fire; only one shell fell, far back in our lines.</p>
<p>We drove on down the road; some snipers fired on us. We were in and out of several houses; some dead were left behind us.</p>
<p>The lorries arrived: <em>Aufsitzen!</em> And so further down the valley.</p>
<p>Our platoon went off to the right; the company commander went a different way, over fairly strongly fortified positions that had to be stormed. A Russian shot the company commander from behind; some Finns fell — the very first of our dead.</p>
<p>On our side we were engaged in clearing out snipers. Terlecher and I spotted one up in a tree. A machine-gun burst went up, and he fired no more.</p>
<p>A Wehrmacht soldier directed us up to our positions by a village. We drove forward and took over the positions from Wehrmacht, who had finished building them.</p>
<p>Rain and mud. We did not see the Russians. They lay in a cornfield and fired on us in the half-light. A kilometre ahead was a village. We lay on a knoll and had no clear view of the hollow below, when we heard the clanking of advancing tanks and the shout: <em>Panzer vorne!</em></p>
<p>We then saw tanks of various kinds rolling forward — a couple extra-large ones, some with more than one turret. One turret was shot off, but the tank drove on. Six or seven of them passed us. We had nothing in the way of anti-tank guns. The nearest tank was 50 metres away. I loaded armour-piercing rounds and fired — without effect. Our 3.5 cm <em>Pak</em> was equally useless. We tried with a mortar; the bomb landed near the brute — nothing more. The tank just drove on past us, far to the rear. It looked rather melancholy.</p>
<p>To our right they shouted that <em>Pak</em> was coming, and a couple drove up. Two shots from the tanks and both our <em>Pak</em>s were instantly out of action.</p>
<p>One tank, on its way back, went for us — it had noticed us on that knoll. One of the gun turrets swung towards us. It flashed; the shot carried away the leg of our machine gun. It looked rather wretched — it was exactly as if the end had come.</p>
<p>But suddenly we heard: "Hurra!" We looked back. There came German tanks rolling forward, and the Russians swung away and withdrew. A roar of jubilation ran along our whole line.</p>
<p>During all this I smoked cigarettes by the packet. It might be the end, and these cigarettes at least should not fall to the Russians.</p>
<p>On the night of 20–21 July, 1941, we were pulled out of the positions and relieved by Wehrmacht, and sent directly towards Kiev. Near Smela there was fairly hard fighting with two assaults for 7th Company. The divisional commander with his entire staff drove past us and was surrounded. We were ordered to attack a height near Smela — 1st and 2nd Platoon of Companies 7 and 11 were committed.</p>
<p>The Russians lay in a copse behind the height, shaped like a horseshoe around it. Before the copse was a dip, a hollow. From the height the Russians used artillery and mortars, and it was for us to run forward at full speed, one by one, and then begin the ascent while the Russians fired at us with everything they had. The mortar shells were particularly unpleasant, whining and whistling about our ears as we worked our way through the cornfield.</p>
<p>We fought our way right up, after a frightful struggle — but still had one last step into the copse. We lay in the bottom of the horseshoe, digging in, while the Russians closed the noose from both sides.</p>
<p>Then it became pitch dark, and we used the darkness to shoot our way out and return to the original height. A patrol next morning found the copse empty.</p>
<p>While we lay on security duty along the Dnieper with a bridge in front of us, we came under fire from the far bank. Here a Finnish officer fell.</p>
<p>The bridge was difficult to cross, but we tried to suppress the fire from houses and gardens on the far bank so we could sprint over. While we lay there and fired, a lunatic came on a motorcycle and drove straight across, onto open ground, while we gave him the best cover we could. A young German soldier, Meier, was ordered to run after him, and refused. So front fighter Svendsen from Tønsberg ran across.</p>
<p>That motorcyclist was the most cold-blooded individual I have ever encountered.</p>
<p>I recall that as we approached the Dnieper, I one day joined a patrol towards the river. Ten men in a lorry; we drove to a small village where some Russian civilians were digging shelter trenches for themselves, since the war had now come their way too. Suddenly the Russians opened up with artillery, and we drove off to a larger village, stopping outside a shop. We went in and carried out what we thought we could use. When we had finished, the Russian civilian population streamed into the shop and helped themselves — a small boy made off carrying the cashbox.</p>
<p>When we had lain in the first village, we were ordered to go forward and locate the Russian artillery positions. We went up a road lined with tall poplar trees. Some 200–300 metres ahead we saw a Russian soldier waving at us. Through binoculars we saw he was holding a rifle, and formed the impression he wished to surrender. We therefore went right up to where he stood — a road junction just in front of a village. But the Russians had dug trenches at the junction, and when we came to where the Russian stood, he jumped down into the trench — which was full of Russians. We assumed they wanted to surrender; naturally it would be rather agreeable to return with a battalion of prisoners. Our section commander therefore climbed up onto the trench parapet, produced a German–Russian phrase-book and tried to make the Russians understand that they should give themselves up — now consulting the book, now addressing the Russians in the trench.</p>
<p>Then it became apparent that the Russians thought <em>we</em> had come to surrender; when they realised their mistake, one of them lobbed a grenade. We flung ourselves down and found cover in the trench; then lay and tossed grenades down into it. The Russians ducked in the trench, and we used that to get away. We ran like blazes and escaped with only 3–4 wounded. There were a great many Russians.</p>
<p>Afterwards we drove for a long time without seeing any more Russians and passed the night in a village.</p>
<p>"Henriksen. Do you remember where there was a bridge through a village — a bridge that had been blown?"</p>
<p>HENRIKSEN: "Yes, I came to it from the transport column, where I had been left as a wounded man."</p>
<p>LARSEN: We reached it one afternoon. From a height we could look down into a valley with a village in it. A patrol had been driven down there earlier in the day and been taken by the Russians. When we later came to the lorry, we found that the Russians had tortured the crew to death: they had put out their eyes, cut off their ears and noses. It was a ghastly sight.</p>
<p>It was decided to attack the village the next day, since it was thought to contain Cossacks.</p>
<p>During the night we lay up on the height. In the morning, when it grew light, our artillery opened up. We had a fine view and saw that the valley on the far side was full of cavalry. I lay beside the artillery observer and heard him calling targets and observing falls, and watched the horses galloping in all directions under the fire. The Russians had no time to reply — only one shell fell, far back in our lines.</p>
<p>We then attacked, but were heavily fired on from across the river. The river was shallow and could be partially waded; we took the village. A great many squadrons were put to flight, and 7th Company's contribution was, by God, mentioned in a special communiqué — so we must have done well enough.</p>
<p>Then came the action I was not part of — the breakthrough — because I had gone down with jaundice in the village.</p>
<p>Once when I took part in a breakthrough, my lorry broke down in the night behind the Russian lines. We stood for several hours, as repair was impossible in the dark. In the morning we got the lorry going again and drove on until we came to a hollow where a Luftwaffe lorry was standing. Its crew dared not drive on, as the nearest height was under Russian bombardment. We pushed on regardless, crossed the height without being hit, and found the road clear ahead.</p>
<p>Then six <em>Ratas</em> appeared and we drove our lorry into a large haycock. The aircraft did not see us, but found the Luftwaffe lorry and bombed it.</p>
<p>When the aircraft were gone, we drove on to a crossroads where two Russian lorries came from the right. In a field was a great mass of cavalry behaving in complete confusion. We fired on both the lorries and the horsemen; the Russian drivers jumped out and fled; the horsemen galloped off down the road we were to take. We went after them and chased them along in front of us until they ran into a village held by our people.</p>
<p>HENRIKSEN: We had in the company 16 Finns who were out on patrol and who were fortunate enough to receive the cavalrymen as they came galloping in — a couple of hundred of them. The Finns let the riders come quite close before they fired. Only five Russians escaped. The Finns then went forward and stripped the fallen of cigarettes and so on. They took no prisoners — Finns generally did not.</p>
<p>LARSEN continues: On the 17th we were out with a patrol well ahead, but not quite to the railway line. We saw some Russians here and there; they evidently thought us many, as we advanced in broad formation.</p>
<p>We saw some horses rear up; when we went towards the Russians they ran. A little firing; we took 6–8 prisoners. A couple of Russians lay where they fell as we went on.</p>
<p>Then we came to the stream Henriksen speaks of and secured a few more Russians there. While we stood talking to them, the Russians seemed rather pleased with themselves. So I looked about, from the stream bed up towards the height — and saw, God help us, Russians swarming in their thousands. We ran for all we were worth, the prisoners too — we took them with us.</p>
<p>Then began the worst week of my life.</p>
<p>It was 35 degrees of frost with a wind. My section had been sent as a patrol to a village, and I stood with Kalischefski at the edge of the village. It was dark. We heard something approaching.</p>
<p>Kalischefski: "Do you hear the Russians?"</p>
<p>I: "Yes."</p>
<p>Kalischefski: "I'm going back to report."</p>
<p>I heard the Russians, but then suddenly a shot — for as Kalischefski ran back to report, he had thrown a grenade over the roof of the house we were standing by, to frighten the Russians, and this grenade fell right in front of me.</p>
<p>So I roared: "<em>Ruki verkh!</em>" (Hands up!)</p>
<p>The Russians called: "<em>Nicht schiessen!</em>" And came forward with their hands up. Kalischefski now returned and we escorted all our prisoners back to the command post.</p>
<p>HENRIKSEN: Our artillery had only 120 shells, but used them well. They fired shot after shot into the midst of the Russians and we watched Russian caps, arms, and legs flying in every direction. The artillery observer up on the height was hit in the head, and the artillery had to manage without him from that point.</p>
<p>LARSEN continues: Kalischefski and I lay together on the height. The Russians fired so heavily we did not dare raise our heads. But we found a box which we stuck up, and it was immediately shot out of our hands.</p>
<p>We lay and talked and smoked. Then it went completely quiet in front of us. Kalischefski peered up and his jaw dropped: <em>Die Russen kommen!</em></p>
<p>And there they were. In their thousands — but no firing.</p>
<p>And we ran. The nearest Russian was not a hundred metres away. Our unit had fallen back and forgotten to warn us.</p>
<p>I can tell you our hearts were in our mouths.</p>
<p>We did not know which way to run. Shells burst around us everywhere. And those great greatcoats we had on hampered us terribly. Kalischefski tried to shed his greatcoat but could not manage it, as he had buckled his belt over it — and there was no time for undressing.</p>
<p>Our section commander was Terlecher. One day he came to us with this order: "I have received orders from the regimental commander to hold this height to the last man."</p>
<p>Whereupon Kalischefski remarked: "As we're done for in any case, I should like at least to be comfortable in my last hour." And distributed all the ammunition from the case he had been carrying.</p>
<p>From the height we had a fine view, and far off we could see something like a fog advancing. It was Russian tanks, cavalry, everything — coming closer and closer.</p>
<p>And we were 12 men with 2 machine guns.</p>
<p>We also had on the hill two artillery observers, but they were so nervous that their hands were shaking, so the section commander sent them back.</p>
<p>When the Russians came within range, we blazed away for all we were worth, and the Russians returned fire. And so we lay and shot.</p>
<p>Then the Russian shells began to come in, and immediately after we had no more ammunition.</p>
<p>We had managed to hold the Russians for a time, and they had begun bringing up artillery. Then the section commander said: "We can't exactly receive them with the bayonet. We're going." And we fell back to the others, who had actually found time to dig positions. We lay there and held the Russians all day.</p>
<p>The next day a new attack came, which actually rolled up the entire line. Then suddenly we were alone. We lay behind a haycock while Russian tanks fired and fired.</p>
<p>Then from behind came a German lorry. We waved to get it out of the way. But it came right up to us. It was the regimental commander, calling: "Hold on! Half an hour more! We're getting German tanks!" We held. And 37 German tanks came and broke the attack on a broad front. We held the position until midnight, then fell back to the Mius. There the Russians halted. At the Mius were depots, food, and ammunition — which was what made it possible to hold that line.</p>
<p>On one occasion — it was Christmas Eve, 1941 — the Russians attacked the Italian sector, killed four hundred, and dug themselves in. But an SS battalion was put in one morning and drove them out again.</p>
<p>One night we stood by a house with a sentry on the loft. The roof had been shot to pieces, giving a good view towards the Russian side. Suddenly we heard a fall up on the loft and understood that the sentry had been hit. A man was sent up as relief — but before he was properly up, he shouted: <em>Die Russen kommen!</em></p>
<p>Up with the machine guns — and there were Russians coming from behind, into the farmyard. But a haycock had been set ablaze and gave a fair light, and we saw a pile of Russians going down. On the whole open ground to my left, Russians were falling and crying out. One of those lying on the ground threw a grenade at us, and I saw him fumbling in his pocket with his hand — I thought: the devil, there'll be another one. But what he took out was not a grenade but a razor — with which he cut his own throat.</p>
<p>Then the Russians ran — into the minefield. There were explosions in the burning haycock, and later we found two dead Russians in it with grenades.</p>
<p>It was a dreadful muddle.</p>
<p>Terlecher then said: "We must clear the house." We went and tossed grenades in, which frightened out a couple of wounded Russians who came crawling.</p>
<p>Dreadful muddle — dead people everywhere. But not one of our section was wounded. Terlecher commanded coolly and steadily — directed and sorted things out. I estimate there were roughly fifty Russians in the attack.</p>""")

T['Legiogri.html'] = (
    'The Norwegian Legion – Organisation and Origins',
    'The Norwegian Legion – Organisation and Origins',
    """\
<p>The Norwegian Legion</p>
<p>(As recounted by Jens Grini)</p>
<p>He volunteered in the summer of 1941 for the Legion and reported to Bjølsen School in Oslo. He did not go with the first contingent of the Legion that departed from Gulskogen, being sent instead to Kongsvinger for training under Captain Ragnar Berg. Not until the 1st of September, 1941, was he — together with several others and under Lindgren's command — sent by sea to Germany, more specifically to the Non-Commissioned Officers' School at Lauenburg in Pomerania. Shortly before Christmas 1941 he joined the Legion at Fallingbostel.</p>
<p>Captains Berg and Lindvig had selected 25–30 men for the contingent in which Jens travelled. In Norway he had attended recruit school as an artillerist; he was now trained as an infantryman and received at Lauenburg a reasonably solid foundation.</p>
<p>On joining the Legion, he was posted to 2nd Company, commanded by Captain Sveen from Biri. In January–February 1942 the Legion was sent by train to Stettin, where it was intended to remain for a time — though it lay there only two or three weeks, during which time a number of new men arrived from Norway.</p>
<p>"Perhaps the reason we did not remain longer in Stettin was that Himmler came and looked us over. Lindvig had had us on a march — it was snowing, wretched weather — and Himmler had turned up to see us. Lindvig spotted him, straightened himself up, and executed the finest march-past imaginable, which Himmler found extremely gratifying. He went round and spoke to the men and asked how the food was. They told him the honest truth — that the food was poor. Himmler tasted it and said: 'This is not good enough!' — and swung up into his car."</p>
<p>A couple of days later the order came to depart by air. The order came suddenly and we had to send out parties through the town to recall all men on leave. Then it was a matter of packing and preparing everything.</p>
<p>Next morning we took the tram to the airfield, where we were loaded, 12–13 men per aircraft. Off we went — the first day to Riga. The aircraft did not continue, as there was snow and fog. The following day we flew at low altitude over Lake Peipus. We were headed for Krasnoye Selo, but had to land short as the fog was extremely thick. Next day we made two attempts to fly on, but both times had to turn back; only on the day following — in a snowstorm and fog — did we reach Krasnoye Selo, or rather the area in which that town lies, the aircraft landing here and there across a wide area. No accidents occurred; only one aircraft made a crash-landing.</p>
<p>And so we were assembled. By lorry we were transported to the village of Pushkin, lying just behind the front. We were billeted in a palace — but within Russian artillery range. The front line was only about 500 metres forward.</p>
<p>I had been assigned to 2nd Company, comprising three platoons. I was in 3rd Platoon, and when we went into the line I was deputy platoon commander under Hervig. I later became section commander with the rank of Unterscharführer — ten men in my section. The spirit in the Legion was excellent. From our position we could see Leningrad.</p>
<p>We lay near Uritsk by the Gulf of Finland, having relieved a mixed German unit. It was a devilishly hard sector we had been given. The Leibstandarte SS Adolf Hitler had been there previously — we took over around the 5th of April.</p>
<p>It was extremely dangerous to look over the parapet, owing to Russian snipers. There was a great deal of snow when we arrived, so the trench parapets were some two metres high. But then there came a violent thaw, and within a couple of days we were standing in trenches only 70 cm deep.</p>
<p>The Germans who had preceded us had been rather restrained in their shooting so as not to provoke the Russians. We felt obliged to shoot. We engaged in sniping with rifles, and eventually got the upper hand of the Russians entirely. "We had them well under our thumb in the end."</p>
<p>I took part in a raiding party that, under Sveen's command, went out 12–13 km onto the Gulf of Finland to sever the communication line between Leningrad and Kronstadt. We were exhausted when we started, for the trenches stood under water while the Russians lay over us the entire time. There were three sections of us, and I commanded one.</p>
<p>We set out in the evening, after dark — around the 10th to 12th of April, 1942. This expedition was one of the most bloodless in the Legion's history. Tiring, but no combat.</p>
<p>We went on skis. It was raining, dark, and partially foggy. Close to shore we waded to the knee, but further out the ice was firmer. The snow was so thoroughly wet that the skis glided tolerably well.</p>
<p>We advanced with the three sections abreast, close enough that each could see its neighbour. I had one of the flank sections. We navigated by compass until we struck the road between Leningrad and Kronstadt, where the telegraph and telephone lines ran. There was no Russian sentry at the point where we arrived. We lay in position for an hour in case the Russians were about — none appeared — then cut the lines and returned. We could not remain on the ice any longer, being soaking wet and completely chilled through.</p>
<p>The expedition was a daring one, since we were in an area commanded by Russian artillery. Had the Russians spotted us, fire from the Leningrad mole could have made our situation decidedly uncomfortable.</p>
<p>We lay in this sector for some seven weeks and during that time were subjected to artillery fire alone. The Russians had, however, discovered that Norwegians were holding the position: Captain Ragnar Berg with some men had fallen on about the 19th of April, I believe. He had been out on patrol, completed his mission, but trod on a Russian minefield on the return.</p>
<p>On the 22nd of April, at 03.30, the Russians opened a artillery bombardment against the Legion. It lasted three hours, and for those three hours shells of every calibre rained down. The bombardment had been carefully prepared, the Russians having been ranging and registering since the 10th of April. It made it extremely difficult to evacuate the wounded from the trenches during the day; we had to lay smoke to get them to the rear.</p>
<p>German artillerists calculated that the weight of shells which had fallen on our sector amounted to thirty railway wagons. When the bombardment was over, the Russians attacked against 1st Company, possibly also against 3rd Company — but were repulsed.</p>
<p>The Legion held the front line from its arrival in February until the 1st of December. On the night of the 1st to 2nd of December it was relieved by the Dutch. The Legion had by then held these positions since the 24th of May and repulsed many attacks. When the Legion was taken back, it was to rest for two or three weeks; I received leave and departed on the 1st of December.</p>
<p>On the night of the 4th of December, the Russians attacked and drove the Dutch out of the position, which they then occupied. The Legion was ordered forward, went in to counter-attack, drove out the Russians, and held the position. I returned to the Legion at the end of January 1943 — to find that my company had suffered severely. Not enough men remained to fill more than one bunker.</p>
<p>In March 1943 the Legion was withdrawn to Latvia, where all were demobilised. The panzergrenadier regiment was then formed, and all who wished went into it.</p>""")

T['Legpans.html'] = (
    'The Norwegian Legion – Tank Destroyers',
    'The Norwegian Legion – Tank Destroyers',
    """\
<p>Tank-Destroyer at the Norwegian Legion</p>
<p>As recounted by Bernt Odmar Larsen</p>
<p>General Jeckel, the commander of the battle group that for a time included the Norwegian Legion, once remarked: "Had there been three army corps of Norwegians on the Eastern Front, the German High Command need have issued no other order than: 'Stop when you reach Vladivostok!'"</p>
<p>Bernt departed on the 2nd of August, 1941, with the second contingent, to Fallingbostel, under the command of Captain Finsen. At Fallingbostel he was initially posted to 3rd Company, which was to form the nucleus of the later tank-destroyer company. This company first stood under the command of Carsten Sveen, who was subsequently appointed commander of 2nd Company. Captain Finsen then took 3rd Company and transformed it into the Legion's tank-destroyer company.</p>
<p>The company had four platoons. It was initially horse-drawn but was motorised on arrival at the front. The armament was the 3.7 cm PAK anti-tank gun. At the front, each platoon had initially four guns, later five. Each gun had a gun commander, four other ranks, and one permanent driver. Each man was armed with a carbine; gun commanders had pistols; platoon commanders and the company commander had sub-machine guns and pistols. At full strength the company mustered 209 men.</p>
<p>At Fallingbostel, exercises were conducted in all military disciplines. The Legion arrived in July–August 1941 and went directly into training, which continued until New Year 1942. The Legion was then sent by train to Stettin, where it was billeted in a former lunatic asylum — a detail that amused the men — for four weeks of finishing exercises, before departing in early February 1942 for the front at Leningrad.</p>
<p>We came into action in the last days of February and the first days of March near a small locality called Finskoe — some 11 km from Leningrad, which we could see ahead of our front. My platoon was placed in the sector of 1st Company, commanded by Olav Lindvig. The platoon commander was Rolf Gilstad, who later became company commander in the Ski Battalion. I served as observation NCO, responsible for determining ranges in the forward area and in general gathering any intelligence useful for fire control against an attacker in our sector. There was, however, little work for the tank-destroyers in this sector; we accordingly acquired the sobriquet 'The Aristocrats of the Front' — a name that was subsequently revised when the fighting started and our uniforms became so battered that we resembled anything but.</p>
<p>At Easter 1942 we were moved to a sector further forward, towards the city of Leningrad itself, covering the small towns of Staropanovo–Uritsk–Peterhof. The tank-destroyers were now spread across the Legion's entire front; but my platoon was placed behind a German police battalion and reinforced with an extra gun. Our platoon commander, Arnfinn Vik — who later became company commander in the Ski Battalion — took over a number of Russian guns in this sector, from 5 cm calibre upward.</p>
<p>In late March 1942 I attended a pioneer course held at Palkolovo near Leningrad, opposite Konstantinovka. It was a crash course, with one NCO and four men from each company. Instruction covered the most commonly used mines, demolition charges, and related matters, as well as the rifle grenade — effective to 250 metres. The Germans used two men to handle the rifle during firing, the weapon's angle of elevation being measured with a spirit level. But NCO Håkon Jøntvedt of the Legion's 4th Company discovered that one man could manage perfectly well, taking the direction with the left eye whilst simultaneously looking across the spirit level with the right. Jøntvedt's method was subsequently used across the entire Eastern Front.</p>
<p>Jøntvedt was one of those who fell out there. He was a first-rate man — a first-class soldier and comrade.</p>
<p>We had in the Legion an NCO named Svenningsen from Oslo, a man full of ideas. I found him one day sitting in the trench philosophising and singing songs; we talked about this and that. "Here I have a curious weapon," he said, and showed me a small catapult. "What on earth is that?" said I. "Watch," said he.</p>
<p>We drove two posts into the ground and attached a car inner tube between them — precisely like the slingshots one made as boys with a rubber band in a forked stick. He pulled the tube back to a mark he had made in the trench wall and placed a stone in the pouch of the sling.</p>
<p>I looked through my observation binoculars as he drew back the sling and released it, and I saw the stone drop square onto the roof of a Russian bunker, raising a cloud of dust.</p>
<p>"You must try it with a grenade," said I.</p>
<p>"I have none left — I have sent them all away already!"</p>
<p>"You may have some of mine," said I, and gave him a couple of cases.</p>
<p>And he fired! It thundered and smoked out in front as he moved along the trench and fired — now from one place, now from another. We were all delighted with the invention and christened it 'Svenningsen's Secret Weapon.'</p>
<p>We were therefore tremendously indignant when he came one day and told us he had been subjected to pressure to desist. "Yesterday, just as I finished and was sitting having a smoke, an officer came up and said: 'Stop doing that. The others might discover it and start doing the same.' But do you know what I replied? I leapt up, came to attention, and said: 'I was under the impression that we were at war!'"</p>
<p>On the 15th of May, 1942, Bernt was wounded by a shell that burst on the bunker roof, and on the 18th of May was transported to hospital at Krasnoye Selo. He was lying in his bunk when the shell arrived and remembers nothing but a flash. He came to his senses in complete chaos in the bunker, but was helped as best could be by a comrade, Rygh from Trøndelag. Both eardrums were burst. He was sent to a specialist in Poland, then to Graz, thence to Holmestrand; he was then treated at Aker War Hospital and on the 31st of October, 1942, was discharged, no longer considered fit for active service.</p>
<p>Bernt is quiet for a moment. Then he says: "I have so many good memories that I do not know what expression to use. I think of those who fell out there, of all my good comrades whose last words were: 'Give my regards to Norway!', 'Give my regards to Quisling!', 'Give my regards to my family!', 'I have done my duty for Norway!' — So many splendid things were said in those last moments that it beggars belief. And these fine young men lying out there in an unknown grave are called traitors back here at home. What a disgrace."</p>
<p>"But I shall never — not as long as I live — forget those men who stood with me out there in the east."</p>""")

T['Skibat.html'] = (
    'The Ski Battalion',
    'The Ski Battalion',
    """\
<p>The Ski Battalion</p>
<h1 id="unnamed-narrator">Anonymous Account</h1>
<p>At the end of October 1943, the Ski Company met its new recruits at Oulu. With that, the Ski Company ceased to exist and the Ski Battalion was formed.</p>
<p>1st Company: Kahrs (Bergen)<br>2nd Company: Skjefstad (Elverum)<br>3rd Company: Steen (Trondheim)<br>4th Company: Uglestad (Drammen)</p>
<p>I joined 1st Company, as deputy section commander, 1st Section, 2nd Platoon.</p>
<p>1st Platoon was a mortar platoon — it had one mortar. 2nd Platoon was the special platoon, with light weapons; each section had a light machine gun, otherwise sub-machine guns or sniper rifles. This platoon was a sort of guard unit tasked with protecting the commander when he was out. 3rd Platoon was a normal platoon with machine guns and sub-machine guns.</p>
<p>On the march we generally advanced in the order 2nd–3rd–1st platoon, with 1st Platoon at the rear.</p>
<p>Shortly before Christmas came the news that the Ski Battalion was to be committed at the front under the command of Sturmbannführer Banner — a fine soldier, though a great pity he drank so much. He was a cold-blooded individual who often took up a position in the line of fire, shouting and gesticulating, giving his orders.</p>
<p>This Banner was in fact the regimental commander; Halle, who came later, became the Ski Battalion's own commander.</p>
<p>Just after Christmas 1943 we were sent from Oulu to the area above the Kestenka crossroads, where we lay just behind the trenches and conducted exercises, having received new men. After a short time we were sent to the front, where we were given our own sector. We first lay on a height called Height 200, where we built ourselves a little settlement of bark huts and remained for six weeks. German units lay in front of us; their task was to hold the line while ours was to patrol. In the event of an alarm, the Ski Battalion would take action. There was no continuous front with trenches — only a series of strongpoints.</p>
<p>We went out on hunting parties, and before reaching the front line we also took part when the entire regiment conducted an attack. As a preliminary, three German punishment companies stationed here were sent forward one day. In one of the companies there were also three Norwegians. These companies were to attack a small Russian outpost of 40 men — which was, however, a miscalculation. The companies encountered not 40 Russians but a couple of thousand, and came off very badly.</p>
<p>When the men came back, they were in rags, some without their tunics — the result of furious close-quarter fighting. Of one company only three men returned. The three Norwegians all came through; one of them even received the Iron Cross. They had not been in the company that was destroyed.</p>
<p>That evening the entire Ski Battalion had been assembled behind a height, and we then advanced together with the regiment. When we came up under the Russian positions we heard shouting, screaming, and the howling of dogs. The Russians sent up signal flares. We crept forward and the entire battalion formed a 'hedgehog position'. There, at about three or four in the morning, wild fighting broke out. A radio message informed us that large Russian reinforcements were on the march.</p>
<p>The Ski Battalion now received orders to advance and support the punishment companies fighting the Russian outpost. While we lay waiting for the advance order, the Russians opened up with their heavy mortars, which snapped off large trees. Thirty-five men were then selected — all of 2nd Platoon — under Gauslå, with me as deputy, to creep right up to the fighting line.</p>
<p>Meanwhile German aircraft had spotted the Russian reinforcements and were bombing them.</p>
<p>We went forward whilst the rest of the battalion remained. We took with us a medical orderly and a runner to maintain contact between Gauslå and myself. We went so far that there was eventually wild fighting all about us. We had to dig in, and when moving forward we crawled slowly with our skis in hand — having taken them off. We worked our way forward a couple of hundred metres, but were spotted by Russian aircraft, and from the main Russian position directly in front of us the Russians bombarded the area with mortars and artillery, razing large parts of the forest.</p>
<p>We therefore fell back. But there were Russians everywhere, so the battalion received orders to retire; we went back along a lake until we were in our positions again on Height 200. We were the last to reach the height and found the battalion in complete disorder.</p>
<p>We then lay on the height for a few days. Then came another alarm; when we advanced, the Russians pulled back. We lay in front of the minefields throughout the night, waiting for a Russian attack that never came.</p>
<p>2nd Company, under Skjefstad, had one day sent out a patrol that ran straight into a Russian ambush just outside our minefield. Two men fell and two were wounded.</p>
<p>How did Gust Jonassen fall? It happened in March 1943. Jonassen had been out on patrol and on returning walked into one of our own minefields. The rule was that when a patrol came in, the forward sentry should signal the safe route, as they had to walk with great precision so as not to tread on the mines — the usable path was often only as wide as a ski track, so the sentries had to be attentive. But the sentry Jonassen encountered had not been attentive enough. He was a German and gave no indication. Jonassen was tired and wet — you know how it is — and gave the order to spread out, whereupon the platoon walked into the minefield and the mines went off. S-mines.</p>
<p>Jonassen was terribly wounded. I helped carry him to the aircraft that was to take him to hospital, but he died in the aircraft.</p>
<p>One child was hit by a bullet in the chest and killed — a fine young lad. A Strand died instantly. Also fell a German who had been the most capable soldier on the entire front, and whom the Germans had nicknamed 'the terror of the Russians'. He was to have gone on leave in two days and was to have been commissioned as an officer.</p>""")

print("Part 1 of translations loaded.")
