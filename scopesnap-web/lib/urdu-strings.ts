/**
 * SnapAI — Urdu translation strings (Pakistan Phase 2)
 *
 * Rules:
 *  - Technical terms (brand names, model numbers, R-32, PSI, µF, etc.) are NEVER
 *    in this map — they always stay in English / Latin characters.
 *  - Numbers always use Western Arabic numerals (0-9), not Eastern Arabic.
 *  - If a key is missing the t() function falls back to the English string.
 */
export const URDU_STRINGS: Record<string, string> = {

  // ── Navigation ──────────────────────────────────────────────────────────────
  "Dashboard":                       "ڈیش بورڈ",
  "New Assessment":                  "نئی تشخیص",
  "Assessments":                     "تشخیصات",
  "History":                         "تاریخ",
  "Settings":                        "ترتیبات",
  "Pricing Database":                "قیمتوں کا ڈیٹا",
  "Log Out":                         "لاگ آؤٹ",
  "Send Feedback":                   "رائے بھیجیں",

  // ── Entry / assess form ─────────────────────────────────────────────────────
  "Fill in job info, then tap the complaint.": "جاب کی معلومات بھریں، پھر شکایت منتخب کریں۔",
  "Job Info (optional)":             "جاب کی معلومات (اختیاری)",
  "Property address (search existing...)":    "پراپرٹی کا پتہ (پرانا تلاش کریں...)",
  "Homeowner name":                  "گھر مالک کا نام",
  "WhatsApp number (0300-1234567)":  "واٹس ایپ نمبر (0300-1234567)",
  "Phone number":                    "فون نمبر",
  "What's the complaint?":           "کیا شکایت ہے؟",
  "Start Diagnostic":                "تشخیص شروع کریں",
  "Brand":                           "برانڈ",
  "Model Series":                    "ماڈل سیریز",
  "Tonnage":                         "ٹن کپیسٹی",
  "Refrigerant Type":                "ریفریجرینٹ کی قسم",
  "Not Sure":                        "یقین نہیں",
  "Confirm & Continue":              "تصدیق کریں اور جاری رکھیں",
  "Skip":                            "چھوڑیں",
  "Photo OCR":                       "تصویر سے پڑھیں",
  "Manual Entry":                    "دستی درج",

  // ── Refrigerant picker hints ─────────────────────────────────────────────────
  "Check the outdoor unit — the refrigerant type is printed on the label near the service ports.":
    "آؤٹ ڈور یونٹ چیک کریں — ریفریجرینٹ کی قسم سروس پورٹ کے قریب لیبل پر لکھی ہوتی ہے۔",
  "Newer units (2023+) are usually R-32. Units installed 2015–2022 are usually R-410A. Older units are R-22.":
    "نئے یونٹ (2023+) عموماً R-32 ہوتے ہیں۔ 2015–2022 کے یونٹ عموماً R-410A ہوتے ہیں۔ پرانے یونٹ R-22 ہوتے ہیں۔",

  // ── Complaint types ──────────────────────────────────────────────────────────
  "Not Cooling":                     "ٹھنڈا نہیں ہو رہا",
  "Not Heating":                     "گرم نہیں ہو رہا",
  "Not Turning On":                  "آن نہیں ہو رہا",
  "Noisy":                           "آواز آ رہی ہے",
  "Water Leaking":                   "پانی ٹپک رہا ہے",
  "Hissing Sound":                   "سیٹی کی آواز",
  "Tripping Breaker":                "بریکر ٹرپ ہو رہا ہے",
  "High Electric Bill":              "بجلی کا بل زیادہ",

  // ── Diagnostic flow ─────────────────────────────────────────────────────────
  "YES":                             "ہاں",
  "NO":                              "نہیں",
  "Next":                            "اگلا",
  "Back":                            "پچھلا",
  "Undo last answer":                "آخری جواب واپس کریں",
  "Submit Reading":                  "ریڈنگ جمع کریں",
  "Take Photo":                      "تصویر لیں",
  "Skip photo":                      "تصویر چھوڑیں",
  "PATH SO FAR":                     "اب تک کا راستہ",
  "Step":                            "مرحلہ",
  "of":                              "میں سے",
  "Back to complaint selection":     "شکایت کے انتخاب پر واپس",
  "Generate Estimate":               "تخمینہ بنائیں",
  "Skip photos, generate estimate anyway": "تصاویر چھوڑیں، تخمینہ بنائیں",

  // ── Estimate options ─────────────────────────────────────────────────────────
  "Good":                            "بنیادی",
  "Better":                          "بہتر",
  "Best":                            "بہترین",
  "Fix Today":                       "آج ٹھیک کریں",
  "Fix + Peace of Mind":             "مرمت + اطمینان",
  "Full Service":                    "مکمل سروس",
  "Temporary Fix":                   "عارضی مرمت",
  "Repair + Extend Life":            "مرمت + عمر بڑھائیں",
  "Consider Replacing":              "تبدیلی پر غور کریں",
  "Emergency Fix":                   "فوری مرمت",
  "Last Repair":                     "آخری مرمت",
  "Replace Immediately":             "فوراً تبدیل کریں",
  "Recommended":                     "تجویز کردہ",
  "Most Popular":                    "سب سے مقبول",
  "Best Value":                      "بہترین قدر",

  // ── Estimate card content ────────────────────────────────────────────────────
  "Repair Estimate":                 "مرمت کا تخمینہ",
  "Parts":                           "پرزہ جات",
  "Labour":                          "مزدوری",
  "Total":                           "کل",
  "Typical":                         "معمول",
  "Why recommended":                 "کیوں تجویز کی گئی",
  "What's included":                 "کیا شامل ہے",
  "5-year comparison":               "5 سال کا موازنہ",
  "Repair now costs":                "ابھی مرمت کی لاگت",
  "New unit costs":                  "نئے یونٹ کی لاگت",
  "Generate Estimate →":             "تخمینہ بنائیں →",

  // ── Report / send ────────────────────────────────────────────────────────────
  "Send to Homeowner":               "گھر مالک کو بھیجیں",
  "Send Report":                     "رپورٹ بھیجیں",
  "Send via WhatsApp":               "واٹس ایپ سے بھیجیں",
  "Send via Email":                  "ای میل سے بھیجیں",
  "Email Address":                   "ای میل",
  "Phone (SMS)":                     "فون (واٹس ایپ)",
  "Report Link":                     "رپورٹ لنک",
  "Copy":                            "نقل کریں",
  "Sending...":                      "بھیجا جا رہا ہے...",
  "Report sent":                     "رپورٹ بھیج دی گئی",
  "View Report":                     "رپورٹ دیکھیں",
  "Enter a WhatsApp number above to enable WhatsApp sending.":
    "واٹس ایپ بھیجنے کے لیے اوپر نمبر درج کریں۔",
  "They'll get a personalized report with all options, pricing, and energy savings.":
    "انہیں تمام آپشنز، قیمتوں اور بچت کے ساتھ ذاتی رپورٹ ملے گی۔",
  "Homeowner Name":                  "گھر مالک کا نام",
  "Auto follow-ups: 24h if not viewed · 48h if viewed · 7 days final check-in.":
    "خودکار فالو اپ: 24 گھنٹے اگر نہ دیکھی · 48 گھنٹے اگر دیکھی · 7 دن آخری چیک۔",

  // ── Fault card names ─────────────────────────────────────────────────────────
  "Capacitor Failure (Non-Inverter)":         "کیپیسیٹر خرابی",
  "Dirty Filter — Restricted Airflow":        "گندہ فلٹر — ہوا کی رکاوٹ",
  "Dirty Filter":                             "گندہ فلٹر",
  "PCB / Inverter Board Failure":             "انورٹر بورڈ خراب",
  "Refrigerant Undercharge / Leak":           "گیس کم / لیک",
  "Refrigerant Leak":                         "گیس لیک",
  "Drain Clog / Water Leak":                  "ڈرین بند / پانی کا رساؤ",
  "Drain Clog":                               "ڈرین بند",
  "Compressor Failure":                       "کمپریسر خراب",
  "Sensor / Thermistor Fault":               "سینسر خراب",
  "Wiring & Communication Fault":            "وائرنگ و کمیونیکیشن خرابی",
  "Fan Motor Failure (Indoor or Outdoor)":   "پنکھے کی موٹر خراب",
  "Frozen Evaporator Coil (Indoor Unit)":    "ان ڈور کوائل جمی ہوئی",
  "Dirty Condenser Coil (Outdoor Unit)":     "کنڈینسر کوائل گندہ",
  "Dirty Condenser Coil — High Pressure":    "کنڈینسر کوائل گندہ — ہائی پریشر",
  "Dirty Indoor Coil / Restricted Airflow":  "ان ڈور کوائل گندہ / ہوا کی رکاوٹ",
  "Voltage Protection Trip (Load-Shedding Damage)": "وولٹیج خرابی (لوڈ شیڈنگ)",
  "Full System Replacement (End of Life)":   "مکمل یونٹ تبدیلی",

  // ── Status labels ────────────────────────────────────────────────────────────
  "Completed":                       "مکمل",
  "Pending":                         "زیر التواء",
  "Sent":                            "بھیجا گیا",
  "In Progress":                     "جاری",
  "Saved":                           "محفوظ",
  "Draft":                           "مسودہ",
  "Approved":                        "منظور شدہ",
  "Viewed":                          "دیکھا گیا",

  // ── General UI ───────────────────────────────────────────────────────────────
  "Search":                          "تلاش",
  "Cancel":                          "منسوخ",
  "Confirm":                         "تصدیق کریں",
  "Save":                            "محفوظ کریں",
  "Close":                           "بند کریں",
  "Loading...":                      "لوڈ ہو رہا ہے...",
  "Loading analytics...":            "تجزیہ لوڈ ہو رہا ہے...",
  "Error":                           "خرابی",
  "Try again":                       "دوبارہ کوشش کریں",
  "Required":                        "ضروری",
  "Optional":                        "اختیاری",
  "today":                           "آج",
  "ago":                             "پہلے",
  "← Back":                         "← پچھلا",
  "Returning Customer":              "پرانا گاہک",
};
