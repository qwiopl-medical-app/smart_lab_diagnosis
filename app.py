import datetime
from io import BytesIO
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام التشخيص المخبري الذكي", page_icon="🔬", layout="centered"
)


# دالة إنتاج تقرير الـ PDF
def generate_pdf_report(patient_info, diagnoses, recommendations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor("#1A365D"),
    )
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10, spaceAfter=5
    )

    story.append(Paragraph("Smart Clinical Laboratory Report", title_style))
    story.append(Spacer(1, 10))

    patient_data = [
        [
            "Patient Age:",
            str(patient_info["age"]),
            "Gender:",
            patient_info["gender"],
        ],
        [
            "Report Date:",
            patient_info["date"],
            "System Version:",
            "v1.0 (Prototype)",
        ],
    ]
    t = Table(patient_data, colWidths=[90, 140, 90, 140])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Diagnostic Findings", header_style))
    if diagnoses:
        for diag in diagnoses:
            story.append(
                Paragraph(
                    f"<b>• Condition:</b> {diag['condition_en']}", body_style
                )
            )
            story.append(
                Paragraph(
                    f"  <b>Confidence:</b> {diag['confidence_en']}", body_style
                )
            )
            story.append(
                Paragraph(
                    f"  <b>Reasoning:</b> {diag['reasoning_en']}", body_style
                )
            )
            story.append(Spacer(1, 6))
    else:
        story.append(
            Paragraph("All tested parameters are within normal limits.", body_style)
        )

    story.append(Spacer(1, 10))

    story.append(Paragraph("Clinical Recommendations", header_style))
    if recommendations:
        for rec in recommendations:
            story.append(Paragraph(f"- {rec['en']}", body_style))
    else:
        story.append(
            Paragraph("- No specific clinical action required.", body_style)
        )

    story.append(Spacer(1, 20))
    disclaimer_style = ParagraphStyle(
        "Disc", parent=styles["Italic"], fontSize=8, textColor=colors.gray
    )
    story.append(
        Paragraph(
            "Disclaimer: This AI/Rule-based report is a clinical decision support tool and does not replace official diagnostic evaluation by a licensed practitioner.",
            disclaimer_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer


# الواجهة الرئيسية
st.title("🔬 نظام دعم القرار للتحاليل المرضية")
st.write(
    "أدخل بيانات المريض والقراءات المخبرية للحصول على تحليل فوري وتقارير قابلة للطباعة."
)
st.markdown("---")

st.sidebar.header("📋 بيانات المريض")
age = st.sidebar.number_input("العمر", min_value=1, max_value=120, value=25)
gender_ar = st.sidebar.selectbox("الجنس", ["أنثى", "ذكر"])
gender_en = "Female" if gender_ar == "أنثى" else "Male"

st.subheader("🧪 نتائج الفحوصات المخبرية")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🩸 صورة الدم (CBC)")
    mcv = st.number_input(
        "MCV (fL)", min_value=0.0, max_value=150.0, value=85.0, step=1.0
    )
    rbc = st.number_input(
        "RBC (10^6/µL)", min_value=0.0, max_value=10.0, value=4.5, step=0.1
    )
    wbc = st.number_input(
        "WBC (10^3/µL)", min_value=0.0, max_value=50.0, value=7.0, step=0.1
    )
    ferritin = st.number_input(
        "Ferritin (ng/mL)",
        min_value=0.0,
        max_value=1000.0,
        value=30.0,
        step=1.0,
    )

with col2:
    st.markdown("### 🧬 إنزيمات الكبد ووظائفه")
    alt = st.number_input(
        "ALT (U/L)", min_value=0.0, max_value=2000.0, value=25.0, step=1.0
    )
    ast = st.number_input(
        "AST (U/L)", min_value=0.0, max_value=2000.0, value=20.0, step=1.0
    )

st.markdown("---")

if st.button("🚀 تحليل النتائج واستخراج التقرير", type="primary"):

    diagnoses = []
    recommendations = []

    if mcv < 80:
        if ferritin < 15:
            diagnoses.append({
                "condition_ar": "أنيميا نقص الحديد (Iron Deficiency Anemia)",
                "condition_en": "Iron Deficiency Anemia (IDA)",
                "confidence_ar": "عالية",
                "confidence_en": "High",
                "reasoning_ar": f"انخفاض MCV ({mcv}) مع انخفاض مخزون الحديد Ferritin ({ferritin})",
                "reasoning_en": f"Low MCV ({mcv}) combined with low Ferritin ({ferritin})",
            })
            recommendations.append({
                "ar": "يُنصح بإجراء فحص Serum Iron و TIBC لتأكيد الخطة العلاجية.",
                "en": "Serum Iron and TIBC tests are recommended to confirm treatment plan.",
            })

        elif rbc > 5.5:
            diagnoses.append({
                "condition_ar": "احتمال سمة الثالاسيميا (Thalassemia Trait)",
                "condition_en": "Suspected Thalassemia Trait",
                "confidence_ar": "متوسطة",
                "confidence_en": "Moderate",
                "reasoning_ar": f"انخفاض MCV ({mcv}) مع ارتفاع عدد كريات الدم الحمراء RBC ({rbc})",
                "reasoning_en": f"Low MCV ({mcv}) with elevated RBC count ({rbc})",
            })
            recommendations.append({
                "ar": "يُنصح بإجراء فحص الترحيل الكهربائي للهيموجلوبين (Hb Electrophoresis).",
                "en": "Hb Electrophoresis is recommended for definitive diagnosis.",
            })

    if wbc > 11.0:
        diagnoses.append({
            "condition_ar": "ارتفاع كريات الدم البيضاء / اشتباه عدوى (Leukocytosis)",
            "condition_en": "Leukocytosis (Suspected Infection/Inflammation)",
            "confidence_ar": "متوسطة إلى عالية",
            "confidence_en": "Moderate to High",
            "reasoning_ar": f"ارتفاع الإجمالي لكريات الدم البيضاء WBC ({wbc})",
            "reasoning_en": f"Elevated total WBC count ({wbc})",
        })
        recommendations.append({
            "ar": "يُنصح بإجراء فحص التمايز Differential WBC وفحص CRP.",
            "en": "Differential WBC count and CRP testing are recommended.",
        })

    if alt > 200 or ast > 200:
        diagnoses.append({
            "condition_ar": "اشتباه التهاب كبد حاد (Acute Hepatitis)",
            "condition_en": "Suspected Acute Hepatitis / Liver Injury",
            "confidence_ar": "عالية",
            "confidence_en": "High",
            "reasoning_ar": f"ارتفاع حاد في إنزيمات الكبد (ALT: {alt}, AST: {ast})",
            "reasoning_en": f"Severe elevation in liver enzymes (ALT: {alt}, AST: {ast})",
        })
        recommendations.append({
            "ar": "يُنصح بإجراء المسح الفيروسي للكبد (Hepatitis Panel A, B, C).",
            "en": "Hepatitis Viral Panel (A, B, C) is strongly recommended.",
        })

    st.header("📊 التقرير التشخيصي المبدئي")

    if diagnoses:
        for diag in diagnoses:
            st.error(f"**التشخيص المتوقع:** {diag['condition_ar']}")
            st.write(f"• **مستوى الثقة:** {diag['confidence_ar']}")
            st.write(f"• **السبب العلمي:** {diag['reasoning_ar']}")
            st.markdown("---")

        st.subheader("💡 التوصيات الطبية")
        for rec in recommendations:
            st.info(rec["ar"])
    else:
        st.success(
            "جميع النتائج المدخلة تقع ضمن الحدود الطبيعية أو لا تظهر أشكالاً مرضية وفق القواعد الحالية."
        )

    patient_info = {
        "age": age,
        "gender": gender_en,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
    }
    pdf_file = generate_pdf_report(patient_info, diagnoses, recommendations)

    st.markdown("### 📥 تصدير التقرير")
    st.download_button(
        label="تحميل التقرير كملف PDF طبّي",
        data=pdf_file,
        file_name=f"Lab_Report_{datetime.date.today()}.pdf",
        mime="application/pdf",
    )

    st.caption(
        "⚠️ **تنبيه:** هذا النظام أداة مساعدة ولا يستبدل التشخيص الطبي المعتمد من الأخصائي."
    )
