import requests
import feedparser
from newspaper import Article
from deep_translator import GoogleTranslator

# بيانات تيليجرام
BOT_TOKEN = "7412592075:AAG8cJkbs9kO6ScO-2lMkfBOEUDX8GSb3SE"
CHAT_ID = "1104470111"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# 1. تنبيهات CVE
def get_latest_cves():
    url = "https://cve.circl.lu/api/last"
    try:
        response = requests.get(url)
        cves = response.json()

        if not isinstance(cves, list) or len(cves) == 0:
            send_telegram_message("⚠️ لم يتم العثور على ثغرات جديدة حاليًا.")
            return

        for cve in cves[:3]:
            if all(k in cve for k in ['id', 'summary', 'cvss', 'Published']):
                msg = f"""
🚨 [ثغرة أمنية جديدة]  
📛 CVE ID: {cve['id']}  
📝 الوصف: {cve['summary']}  
📊 مستوى الخطورة (CVSS): {cve['cvss']}  
🗓️ تاريخ النشر: {cve['Published']}  
🔗 التفاصيل: https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve['id']}

📘 شرح مبسط:
الثغرة تسمح للمهاجم بالتحكم في النظام أو تنفيذ أوامر عن بعد. يُنصح بتحديث البرنامج المتأثر فورًا.
"""
                send_telegram_message(msg)
            else:
                send_telegram_message("⚠️ تم تجاهل ثغرة بسبب نقص في البيانات.")
    except Exception as e:
        send_telegram_message(f"⚠️ فشل في تحميل CVE من API:\n{e}")

# 2. استخراج + ترجمة
def extract_summary_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text[:500]

        keywords = ['DNS', 'CVE', 'RCE', 'Chrome', 'Botnet', 'Cisco', 'Microsoft', 'Akamai',
                    'Infoblox', 'Amazon S3', 'Azure', 'CDC', 'TDS', 'Malware']

        for word in keywords:
            text = text.replace(word, f'[[[{word}]]]')

        translated = GoogleTranslator(source='en', target='ar').translate(text)

        for word in keywords:
            translated = translated.replace(f'[[[{word}]]]', word)

        return translated
    except Exception as e:
        return f"⚠️ فشل في استخراج أو ترجمة الشرح: {e}"

# 3. أخبار Hacker News
def get_hackernews():
    feed = feedparser.parse("https://thehackernews.com/rss.xml")
    for entry in feed.entries[:3]:
        summary = extract_summary_from_url(entry.link)
        msg = f"""
📰 [خبر سيبراني جديد]  
📌 العنوان: {entry.title}  
📅 التاريخ: {entry.published}  
🔗 اقرأ الخبر: {entry.link}

📘 شرح مبسط:
{summary}
"""
        send_telegram_message(msg)

# 🚀 تشغيل
get_latest_cves()
get_hackernews()
