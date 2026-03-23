import time
import subprocess
from pathlib import Path

BASE      = Path(__file__).resolve().parent
AUDIO_DIR = BASE / "sample_data" / "audio"
CHAT_DIR  = BASE / "sample_data" / "chats"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)

# Format per call id
FMT = {1:"mp3", 2:"wav", 3:"mp3", 4:"wav", 5:"m4a",
       6:"mp3", 7:"wav", 8:"m4a", 9:"mp3", 10:"wav"}

# ══════════════════════════════════════════════════════════════
# 10 CALL LOGS
# ══════════════════════════════════════════════════════════════
CALL_LOGS = [

# ── Grade A ───────────────────────────────────────────────────
{
  "id": 1, "grade": "A", "industry": "Banking",
  "scenario": "Fraud dispute resolved instantly with full empathy",
  "script": [
    ("Agent",    "Thank you for calling First National Bank, this is Priya. How can I help you today?"),
    ("Customer", "Hi Priya. I am really worried. I just noticed a charge of 340 dollars on my account that I did not make."),
    ("Agent",    "I completely understand how alarming that feels and I am really glad you called right away. Let me pull up your account immediately."),
    ("Customer", "Please hurry. I am scared I am going to lose my money."),
    ("Agent",    "I can see the transaction now and it does look suspicious based on the merchant location. I am placing an immediate block on your card right now to stop any further charges."),
    ("Customer", "Oh thank goodness. Will I get my money back?"),
    ("Agent",    "Absolutely yes. Because you reported this promptly you are fully covered under our zero liability policy. I am raising a dispute right now and you will receive a provisional credit within 24 hours while we investigate."),
    ("Customer", "24 hours is incredibly fast. Thank you so much."),
    ("Agent",    "Of course. I am also ordering a replacement card arriving in 3 to 5 days and activating Apple Pay for you so you can still make purchases today."),
    ("Customer", "You have been absolutely amazing. I feel so relieved."),
    ("Agent",    "I am so glad I could help. You are fully protected. Have a wonderful rest of your day."),
  ]
},

{
  "id": 2, "grade": "A", "industry": "E-commerce",
  "scenario": "Lost package resolved with next day redelivery and credit",
  "script": [
    ("Agent",    "Thank you for contacting ShopFast support, I am Alex. How can I help you today?"),
    ("Customer", "Hi Alex. My package was supposed to arrive 4 days ago and it still has not come. I needed it for a birthday this weekend."),
    ("Agent",    "I am so sorry to hear that, especially with a birthday coming up. Let me check the tracking status for you right now."),
    ("Customer", "The tracking has just said in transit for days. Nothing has changed."),
    ("Agent",    "I can see the package has been stuck at our regional sorting facility. This is entirely our fault and I want to make it right for you immediately. I can either arrange express redelivery guaranteed by tomorrow morning or process a full refund right now. Which would you prefer?"),
    ("Customer", "Can you really guarantee tomorrow morning?"),
    ("Agent",    "I am confirming that right now with our priority team. Yes, confirmed before 10am tomorrow. I am also adding a 20 dollar store credit to your account and upgrading your delivery to premium free of charge for the next 6 months."),
    ("Customer", "That is far more than I expected. Thank you so much Alex."),
    ("Agent",    "You deserve it. This was our mistake and I want to make sure you have a wonderful birthday celebration. You will get a confirmation text shortly."),
  ]
},

# ── Grade B ───────────────────────────────────────────────────
{
  "id": 3, "grade": "B", "industry": "Telecom",
  "scenario": "Unexpected bill explained and better plan applied",
  "script": [
    ("Agent",    "Thank you for calling Velocity Mobile, this is James. How can I help?"),
    ("Customer", "Hi James. My bill this month is 45 dollars higher than normal and I cannot understand why."),
    ("Agent",    "I am sorry to hear that. Let me look at your account now."),
    ("Customer", "I have been a loyal customer for 4 years. This has never happened before."),
    ("Agent",    "I can see the reason. There are roaming charges from calls made to Canada on the 14th. On your current plan those are charged at 25 cents per minute."),
    ("Customer", "Oh right. My sister lives in Canada. I completely forgot that would cost extra."),
    ("Agent",    "Totally understandable. Our North America add-on covers all Canada and Mexico calls for just 15 dollars extra per month. Given how often you call Canada it would save you money overall. Can I switch you to that plan?"),
    ("Customer", "Yes please. That makes sense."),
    ("Agent",    "Done. Takes effect from your next billing cycle. Is there anything else I can help you with today?"),
    ("Customer", "No, that is perfect. Thank you James."),
  ]
},

{
  "id": 4, "grade": "B", "industry": "Travel",
  "scenario": "Cancelled flight rebooked with hotel arranged",
  "script": [
    ("Agent",    "Thank you for calling SkyWings. My name is Chris. How can I assist you today?"),
    ("Customer", "My flight got cancelled and I have an important meeting tomorrow that I absolutely cannot miss."),
    ("Agent",    "I am really sorry about the cancellation. Let me look at your booking right away. Can I have your reference number please?"),
    ("Customer", "It is SKY dash 298471."),
    ("Agent",    "I can see the cancellation. There is a connecting flight tonight at 10pm which arrives tomorrow at 9am. That gives you plenty of time for an afternoon meeting. No additional charge since this was our cancellation."),
    ("Customer", "Yes, let us book that one. Is there a hotel covered for tonight?"),
    ("Agent",    "Yes, I am booking a complimentary hotel near the airport for tonight right now. All details will come to your email within a few minutes."),
    ("Customer", "That is a real relief. Thank you Chris."),
    ("Agent",    "My pleasure. Is there anything else I can help with?"),
    ("Customer", "No, that covers everything. Thank you."),
  ]
},

# ── Grade C ───────────────────────────────────────────────────
{
  "id": 5, "grade": "C", "industry": "Retail",
  "scenario": "Return processed correctly but agent cold and robotic",
  "script": [
    ("Agent",    "RetailPlus support. What do you need?"),
    ("Customer", "Hi. I want to return a jacket I bought. The zipper broke after wearing it twice."),
    ("Agent",    "Order number."),
    ("Customer", "It is RP dash 77421."),
    ("Agent",    "It is within the return window. I will send a return label to your email."),
    ("Customer", "Will I get a refund or replacement?"),
    ("Agent",    "Either. You choose on the return form."),
    ("Customer", "How long will a refund take?"),
    ("Agent",    "7 to 10 days after we receive it."),
    ("Customer", "That is quite long. Is there any way to speed it up?"),
    ("Agent",    "No. That is standard."),
    ("Customer", "Okay. Fine."),
    ("Agent",    "Anything else?"),
    ("Customer", "No."),
    ("Agent",    "Okay."),
  ]
},

{
  "id": 6, "grade": "C", "industry": "Utility",
  "scenario": "High bill explained but customer left feeling unsupported",
  "script": [
    ("Agent",    "PowerCo billing support."),
    ("Customer", "My electricity bill is double what it normally is. Something must be wrong."),
    ("Agent",    "Account number?"),
    ("Customer", "PWR dash 882947."),
    ("Agent",    "Your usage was 847 units. Normal is 420. Bill is correct."),
    ("Customer", "I genuinely do not understand how I used twice the electricity. Nothing changed."),
    ("Agent",    "Appliances use more in winter sometimes."),
    ("Customer", "It has not been especially cold. Could the meter be wrong?"),
    ("Agent",    "You can request a meter check. There is a 65 dollar fee unless the meter is found faulty."),
    ("Customer", "I have to pay to check if your meter is wrong? That feels very unfair."),
    ("Agent",    "That is the policy. Do you want to book it or not?"),
    ("Customer", "Fine. Book it."),
    ("Agent",    "Next week. Confirmation by text."),
  ]
},

# ── Grade D ───────────────────────────────────────────────────
{
  "id": 7, "grade": "D", "industry": "Insurance",
  "scenario": "Storm damage claim mishandled with no emergency help offered",
  "script": [
    ("Agent",    "Shield Insurance. Claim number?"),
    ("Customer", "I do not have one. I need to file a new claim. My roof was torn off in last night's storm and rain is getting into my house right now."),
    ("Agent",    "Use the app for new claims."),
    ("Customer", "I do not have the app. I am calling because my house is actively being damaged."),
    ("Agent",    "Fine. Policy number."),
    ("Customer", "PL dash 9928471. Please hurry, this is urgent."),
    ("Agent",    "What is the damage."),
    ("Customer", "Part of the roof is gone. Rain is soaking my ceiling and furniture. I need emergency help today not in weeks."),
    ("Agent",    "Assessor can come in 2 to 3 weeks."),
    ("Customer", "That is unacceptable. What about emergency assistance? My policy should cover that."),
    ("Agent",    "Not sure if your policy covers it. You would need to call back tomorrow to check."),
    ("Customer", "You are telling me to call back tomorrow when my roof is open to the rain right now?"),
    ("Agent",    "I cannot confirm coverage without reviewing the full policy. Call back tomorrow."),
  ]
},

{
  "id": 8, "grade": "D", "industry": "SaaS",
  "scenario": "Ongoing technical issue dismissed with no real solution",
  "script": [
    ("Agent",    "Tech support. What is the issue?"),
    ("Customer", "My internet integration has been failing every few hours for 2 weeks. I work from home and it is seriously affecting my job."),
    ("Agent",    "Have you tried restarting?"),
    ("Customer", "Yes, many times. I have called twice already and nothing has been fixed."),
    ("Agent",    "Try restarting again."),
    ("Customer", "I just told you I have restarted many times. I need an actual solution."),
    ("Agent",    "I can raise a ticket."),
    ("Customer", "I need a technician to come and fix this properly."),
    ("Agent",    "Technician visit costs 99 dollars."),
    ("Customer", "Why would I pay 99 dollars for a fault that is clearly on your side?"),
    ("Agent",    "We do not know it is our fault yet."),
    ("Customer", "My neighbour on the same provider has the exact same problem. It is your network."),
    ("Agent",    "I will raise a ticket. Someone will respond in 48 hours."),
    ("Customer", "48 hours is completely unacceptable for a 2 week problem."),
  ]
},

# ── Grade F ───────────────────────────────────────────────────
{
  "id": 9, "grade": "F", "industry": "Banking",
  "scenario": "GDPR violation - agent collects CVV and demands PIN",
  "script": [
    ("Agent",    "Bank helpline."),
    ("Customer", "Hi. I am having trouble completing an online payment. It keeps failing."),
    ("Agent",    "Give me your full card number."),
    ("Customer", "Is it safe to give that over the phone?"),
    ("Agent",    "Yes it is fine. Standard procedure."),
    ("Customer", "Okay. It is 4532 8821 4471 0092."),
    ("Agent",    "CVV. The 3 digits on the back."),
    ("Customer", "You need my CVV? That seems unusual."),
    ("Agent",    "We need it to verify. Give it to me."),
    ("Customer", "It is 341."),
    ("Agent",    "Now your 4 digit PIN."),
    ("Customer", "My PIN? I should not give my PIN over the phone."),
    ("Agent",    "I cannot help you without it. It is required."),
    ("Customer", "Something is very wrong here. I am hanging up and calling the official number."),
    ("Agent",    "That is a waste of time. Just give me the PIN and I will fix it now."),
    ("Customer", "No. I am hanging up right now."),
  ]
},

{
  "id": 10, "grade": "F", "industry": "Telecom",
  "scenario": "Rude agent, escalation refused, customer abused",
  "script": [
    ("Agent",    "ConnectPlus support. What do you want?"),
    ("Customer", "Hi. I have been incorrectly charged for a cancelled service for 3 months. I have called twice with no resolution."),
    ("Agent",    "System shows it is active."),
    ("Customer", "That is wrong. I have the cancellation confirmation email."),
    ("Agent",    "Cannot see your emails. System is the system."),
    ("Customer", "This is my third call. I want to speak to a manager right now."),
    ("Agent",    "Managers do not deal with this."),
    ("Customer", "Then transfer me to someone who does."),
    ("Agent",    "Cannot transfer. Technical issues."),
    ("Customer", "Every call I get a different excuse. This is completely unacceptable."),
    ("Agent",    "You probably did not cancel it properly. Not my problem."),
    ("Customer", "How dare you. I have the cancellation email right here."),
    ("Agent",    "Whatever. Anything else?"),
    ("Customer", "I am reporting this to the regulator."),
    ("Agent",    "Go ahead."),
  ]
},

]  # end CALL_LOGS


# ══════════════════════════════════════════════════════════════
# 10 CHAT TRANSCRIPTS
# ══════════════════════════════════════════════════════════════
CHAT_LOGS = [

# ── Grade A ───────────────────────────────────────────────────
{
  "id": 1, "grade": "A", "industry": "Healthcare",
  "scenario": "Wrong bill corrected immediately with written confirmation",
  "lines": [
    ("Agent",    "Thank you for contacting MediCare Billing chat. I am Sophie. How can I help you today?"),
    ("Customer", "Hi Sophie. I received a bill for 800 dollars but my insurance was supposed to cover everything. I am really worried. I am on a fixed income."),
    ("Agent",    "I am so sorry this has caused you worry. Please do not panic at all. Let me look at your account right now."),
    ("Customer", "I have not been sleeping because of this."),
    ("Agent",    "I completely understand. I can see exactly what happened. Our billing team used the wrong procedure code. That is entirely our mistake, not yours. You owe absolutely nothing."),
    ("Customer", "Really? So the 800 dollars just goes away?"),
    ("Agent",    "Yes completely. I am resubmitting the correct claim right now and placing a hold on this bill so you will not receive any further notices or calls. I am also sending you a written confirmation to your email this moment so you have it in writing."),
    ("Customer", "I cannot believe it was just a mistake on your end. Thank you so much Sophie."),
    ("Agent",    "Please do not worry at all. You will see the zero balance confirmation in your inbox shortly. Have a peaceful evening."),
  ]
},

{
  "id": 2, "grade": "A", "industry": "SaaS",
  "scenario": "Critical outage handled urgently with data export sent",
  "lines": [
    ("Agent",    "Hi! DataFlow support here. I am Marcus. What can I help you with?"),
    ("Customer", "Marcus, our whole team is locked out of the platform. We have a client presentation in 90 minutes and all our data is inside."),
    ("Agent",    "I can see the issue right now. There was a certificate update this morning that affected authentication. Our engineers are already on it and the fix ETA is 20 minutes. I am escalating your case to critical priority immediately."),
    ("Customer", "20 minutes is okay but what if it runs over? My career is on the line here."),
    ("Agent",    "I completely understand. As a backup I am generating a read-only export of your key dashboards right now and sending it to your email. You will have something to present regardless of timing."),
    ("Customer", "You are sending the export right now? That is above and beyond."),
    ("Agent",    "Access restored. Just confirmed on our end. Please try logging in now."),
    ("Customer", "Yes! It is working! You genuinely saved us today. Thank you Marcus."),
    ("Agent",    "So glad we got there in time. Good luck with the presentation!"),
  ]
},

# ── Grade B ───────────────────────────────────────────────────
{
  "id": 3, "grade": "B", "industry": "Retail",
  "scenario": "Defective product exchanged with prepaid return label",
  "lines": [
    ("Agent",    "Hi, StyleHub support here. I am Nina. How can I help?"),
    ("Customer", "Hi Nina. I bought a jacket 3 weeks ago and the zipper broke after wearing it twice."),
    ("Agent",    "I am sorry about that. A broken zipper that quickly is a clear manufacturing defect. What is your order number?"),
    ("Customer", "SH 88742."),
    ("Agent",    "Found it. Since it is a defect we will cover return shipping completely. I can do a full refund or send the same jacket again. Which do you prefer?"),
    ("Customer", "Same jacket please if it is in stock."),
    ("Agent",    "It is in stock. Prepaid return label is going to your email now. Once we receive the faulty jacket your replacement ships within 24 hours."),
    ("Customer", "That is quicker than I expected. Thank you Nina."),
    ("Agent",    "Of course. Sorry about the defect. Is there anything else?"),
    ("Customer", "No, that is everything. Thanks."),
  ]
},

{
  "id": 4, "grade": "B", "industry": "Food Delivery",
  "scenario": "Wrong order sent, replacement and refund both given",
  "lines": [
    ("Agent",    "FoodRush support here. How can I help?"),
    ("Customer", "I ordered a vegetarian meal and received a meat dish. I am vegetarian. This is really upsetting."),
    ("Agent",    "I am sincerely sorry about that. Getting the wrong meal especially with a dietary requirement is completely unacceptable. Let me fix this right now."),
    ("Customer", "Can I get a replacement or a refund?"),
    ("Agent",    "Both. I am sending a replacement vegetarian order now and issuing a full refund. You should not pay for something you cannot eat. I am also adding a 10 dollar credit for the inconvenience."),
    ("Customer", "Both a refund and a replacement? That is very fair. Thank you."),
    ("Agent",    "The replacement will arrive in about 35 minutes. Again I am really sorry for this mistake."),
    ("Customer", "Thank you for sorting it so quickly."),
  ]
},

# ── Grade C ───────────────────────────────────────────────────
{
  "id": 5, "grade": "C", "industry": "Banking",
  "scenario": "Fee waived but agent short and unhelpful in tone",
  "lines": [
    ("Agent",    "City Bank support."),
    ("Customer", "Hi. I have an unexpected fee on my account this month."),
    ("Agent",    "Account number?"),
    ("Customer", "774421983."),
    ("Agent",    "Maintenance fee. Balance dropped below 500."),
    ("Customer", "I did not know about that. Can it be waived?"),
    ("Agent",    "Once. Done."),
    ("Customer", "How do I avoid it in future?"),
    ("Agent",    "Keep balance above 500 or set up direct deposit. Online banking, account settings."),
    ("Customer", "Okay. Thank you."),
    ("Agent",    "Anything else?"),
    ("Customer", "No."),
  ]
},

{
  "id": 6, "grade": "C", "industry": "E-commerce",
  "scenario": "Late delivery acknowledged but no real compensation offered",
  "lines": [
    ("Agent",    "QuickShip support. What is your issue?"),
    ("Customer", "My order is 4 days late. I needed it urgently and it still has not arrived."),
    ("Agent",    "Order number?"),
    ("Customer", "QS 664219."),
    ("Agent",    "It is in transit. Weather delays."),
    ("Customer", "Can you give me an actual date?"),
    ("Agent",    "About 2 more days."),
    ("Customer", "Can I get any compensation for the delay?"),
    ("Agent",    "Free shipping on your next order."),
    ("Customer", "That is it for a week long delay?"),
    ("Agent",    "That is our policy."),
    ("Customer", "Fine. Whatever."),
  ]
},

# ── Grade D ───────────────────────────────────────────────────
{
  "id": 7, "grade": "D", "industry": "Telecom",
  "scenario": "2 weeks of outages, agent offers no real fix",
  "lines": [
    ("Agent",    "Support chat. What is the problem?"),
    ("Customer", "My internet cuts out every few hours for 2 weeks. I work from home. This is affecting my job badly."),
    ("Agent",    "Have you restarted the router?"),
    ("Customer", "Yes many times. I have also called twice and nothing has been fixed."),
    ("Agent",    "Try restarting it again."),
    ("Customer", "I just told you I have restarted it many times. My neighbour on the same provider has the same problem. It is clearly your network."),
    ("Agent",    "I can raise a ticket. Manager response in 48 hours."),
    ("Customer", "48 hours is unacceptable for a 2 week ongoing issue. I need this fixed now."),
    ("Agent",    "That is our response time."),
    ("Customer", "This is terrible service. I am looking at other providers."),
    ("Agent",    "That is your choice."),
  ]
},

{
  "id": 8, "grade": "D", "industry": "Retail",
  "scenario": "Loyalty points dispute dismissed, customer ignored",
  "lines": [
    ("Agent",    "Rewards support."),
    ("Customer", "Hi. I spent 500 dollars last month and my loyalty points were never added. It has been 35 days."),
    ("Agent",    "Points take 30 days. There are sometimes delays."),
    ("Customer", "It has been 35 days. That is not a useful answer. Can you check?"),
    ("Agent",    "Need receipts to investigate."),
    ("Customer", "It was all online. My order history is right there in my account."),
    ("Agent",    "Different system. I can raise a ticket. 10 to 15 business days."),
    ("Customer", "3 weeks to fix something automatic? I have spent hundreds here. This is why I am thinking of switching."),
    ("Agent",    "That is your decision."),
  ]
},

# ── Grade F ───────────────────────────────────────────────────
{
  "id": 9, "grade": "F", "industry": "SaaS",
  "scenario": "Data loss dismissed as user error, no help given",
  "lines": [
    ("Agent",    "Tech support."),
    ("Customer", "Hi. I lost 3 months of client data after your update last night. This is catastrophic for my business."),
    ("Agent",    "Maintenance was scheduled and announced."),
    ("Customer", "I received no announcement. And an update should not delete user data."),
    ("Agent",    "You probably deleted it yourself."),
    ("Customer", "I did not. This is 3 months of client records. Can you restore from backup?"),
    ("Agent",    "Backups are for system data not user files."),
    ("Customer", "I need your supervisor and your legal contact immediately."),
    ("Agent",    "I do not have that information."),
    ("Customer", "You work here and do not have your own company legal contact?"),
    ("Agent",    "Not at my level. Anything else?"),
  ]
},

{
  "id": 10, "grade": "F", "industry": "Travel",
  "scenario": "Refund withheld for 5 weeks after airline cancellation",
  "lines": [
    ("Agent",    "Travel support."),
    ("Customer", "Hi. You cancelled my flight 5 weeks ago and I still have not received my refund."),
    ("Agent",    "Refunds take up to 12 weeks."),
    ("Customer", "Consumer law requires refunds within 7 days for cancellations you initiated. It has been 5 weeks."),
    ("Agent",    "Our policy is 12 weeks."),
    ("Customer", "Your policy cannot override consumer law. I have been escalated to billing 3 times with no result."),
    ("Agent",    "I do not have visibility on billing."),
    ("Customer", "This is 800 dollars you are withholding. I want written confirmation of the delay reason."),
    ("Agent",    "I cannot provide that."),
    ("Customer", "I am filing a chargeback and a complaint with the aviation regulator right now."),
    ("Agent",    "Okay."),
  ]
},

]  # end CHAT_LOGS


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def check_ffmpeg() -> bool:
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def convert_audio(src: Path, dst: Path) -> bool:
    ext = dst.suffix.lower()
    if ext == ".wav":
        cmd = ["ffmpeg", "-y", "-i", str(src),
               "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", str(dst)]
    elif ext in (".m4a", ".mp4"):
        cmd = ["ffmpeg", "-y", "-i", str(src),
               "-vn", "-acodec", "aac", "-ab", "128k", "-f", "mp4", str(dst)]
    else:
        return False
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return r.returncode == 0


def make_audio(call: dict):
    from gtts import gTTS
    fmt   = FMT[call["id"]]
    name  = f"call_{call['id']:02d}"
    tmp   = AUDIO_DIR / f"{name}_tmp.mp3"
    final = AUDIO_DIR / f"{name}.{fmt}"

    # Clean up any leftover tmp file from previous failed run
    if tmp.exists():
        tmp.unlink()

    if final.exists():
        print(f"    skip  {final.name} already exists")
        return final

    text = "  ".join(f"{s} says: {t}" for s, t in call["script"])

    saved = False
    for attempt in range(1, 4):
        try:
            gTTS(text=text, lang="en", slow=False).save(str(tmp))
            saved = True
            break
        except Exception as e:
            wait = attempt * 8
            print(f"    warn  gTTS attempt {attempt} failed: {e}")
            if attempt < 3:
                print(f"    wait  {wait}s before retry...")
                time.sleep(wait)

    if not saved:
        print(f"    fail  all gTTS attempts failed")
        return None

    if fmt == "mp3":
        if final.exists(): final.unlink()
        tmp.rename(final)
    else:
        if check_ffmpeg():
            ok = convert_audio(tmp, final)
            if tmp.exists(): tmp.unlink()
            if not ok:
                final = AUDIO_DIR / f"{name}.mp3"
                if final.exists(): final.unlink()
                tmp.rename(final)
                print(f"    warn  ffmpeg failed, saved as .mp3")
        else:
            final = AUDIO_DIR / f"{name}.mp3"
            if final.exists(): final.unlink()
            tmp.rename(final)
            print(f"    warn  ffmpeg not found, saved as .mp3")

    return final


def write_chat(chat: dict) -> Path:
    path = CHAT_DIR / f"chat_{chat['id']:02d}.txt"
    path.write_text(
        "\n".join(f"{s}: {t}" for s, t in chat["lines"]),
        encoding="utf-8"
    )
    return path


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    print("\n" + "="*52)
    print("  CallAudit Pro - Dataset Generator")
    print("  10 Call Logs (audio) + 10 Chats (txt)")
    print("="*52)

    try:
        import gtts
        print("\n  OK   gTTS   : ready")
    except ImportError:
        print("\n  FAIL gTTS not installed")
        print("       Run: pip install gtts")
        return

    if check_ffmpeg():
        print("  OK   ffmpeg : ready")
    else:
        print("  WARN ffmpeg : not found - audio saved as .mp3")
        print("       Install: winget install ffmpeg")

    print(f"\n  File naming:")
    print(f"    Audio  -> call_01.mp3  call_02.wav  ... call_10.wav")
    print(f"    Chats  -> chat_01.txt  chat_02.txt  ... chat_10.txt")

    # ── Audio ──────────────────────────────────────────────────
    print(f"\n{'-'*52}")
    print("  CALL LOGS -> sample_data/audio/")
    print(f"{'-'*52}")

    for call in CALL_LOGS:
        fmt = FMT[call["id"]]
        print(f"\n  call_{call['id']:02d}.{fmt}  |  Grade {call['grade']}  |  {call['industry']}")
        print(f"  {call['scenario']}")
        path = make_audio(call)
        if path and path.exists():
            kb = path.stat().st_size // 1024
            print(f"  done  {path.name} ({kb} KB)")
        else:
            print(f"  fail")
        time.sleep(5)

    # ── Chats ──────────────────────────────────────────────────
    print(f"\n{'-'*52}")
    print("  CHAT TRANSCRIPTS -> sample_data/chats/")
    print(f"{'-'*52}")

    for chat in CHAT_LOGS:
        print(f"\n  chat_{chat['id']:02d}.txt  |  Grade {chat['grade']}  |  {chat['industry']}")
        print(f"  {chat['scenario']}")
        path = write_chat(chat)
        print(f"  done  {path.name} ({len(chat['lines'])} lines)")

    # ── Summary ────────────────────────────────────────────────
    audio = sorted(AUDIO_DIR.glob("call_0*.mp3")) + \
            sorted(AUDIO_DIR.glob("call_0*.wav")) + \
            sorted(AUDIO_DIR.glob("call_0*.m4a"))
    chats = sorted(CHAT_DIR.glob("chat_0*.txt"))

    print(f"\n{'='*52}")
    print(f"  COMPLETE\n")
    print(f"  sample_data/audio/ -> {len(audio)} files")
    for f in sorted(audio, key=lambda x: x.name):
        print(f"    {f.name}")
    print(f"\n  sample_data/chats/ -> {len(chats)} files")
    for f in chats:
        print(f"    {f.name}")
    print(f"\n{'='*52}\n")


if __name__ == "__main__":
    main()