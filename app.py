import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('vault_data.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS entries(username TEXT, date TEXT, title TEXT, category TEXT, description TEXT, impact INTEGER)')
conn.commit()

# --- وظائف مساعدة ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- واجهة التطبيق ---
st.set_page_config(page_title="خزنة المعنويات الاحترافية", page_icon="🔒")

def main():
    st.title("✨ منصة ذكرياتك المعنوية")
    
    menu = ["تسجيل الدخول", "إنشاء حساب جديد"]
    choice = st.sidebar.selectbox("القائمة", menu)

    if choice == "إنشاء حساب جديد":
        st.subheader("إنشاء حساب جديد")
        new_user = st.text_input("اسم المستخدم")
        new_password = st.text_input("كلمة المرور", type='password')

        if st.button("تسجيل"):
            try:
                c.execute('INSERT INTO users(username,password) VALUES (?,?)', (new_user, make_hashes(new_password)))
                conn.commit()
                st.success("تم إنشاء الحساب بنجاح! انتقل لتسجيل الدخول.")
            except:
                st.warning("اسم المستخدم موجود مسبقاً.")

    elif choice == "تسجيل الدخول":
        username = st.sidebar.text_input("اسم المستخدم")
        password = st.sidebar.text_input("كلمة المرور", type='password')
        
        if st.sidebar.checkbox("دخول"):
            c.execute('SELECT password FROM users WHERE username =?', (username,))
            result = c.fetchone()
            
            if result and check_hashes(password, result[0]):
                st.success(f"مرحباً بك يا {username}")
                
                # نموذج الإدخال للمستخدم المسجل
                with st.expander("➕ أضف ذكرى معنوية جديدة"):
                    with st.form("entry_form", clear_on_submit=True):
                        title = st.text_input("العنوان")
                        cat = st.selectbox("التصنيف", ["امتنان", "إنجاز", "إلهام"])
                        desc = st.text_area("التفاصيل")
                        imp = st.slider("الأثر", 1, 10, 5)
                        submit = st.form_submit_button("حفظ في خزنتي")
                        
                        if submit and title:
                            date = datetime.now().strftime("%Y-%m-%d")
                            c.execute('INSERT INTO entries VALUES (?,?,?,?,?,?)', (username, date, title, cat, desc, imp))
                            conn.commit()
                            st.balloons()

                # عرض بيانات هذا المستخدم فقط
                st.subheader("📜 سجل ذكرياتك الخاصة")
                user_data = pd.read_sql_query(f"SELECT date, title, category, description, impact FROM entries WHERE username='{username}'", conn)
                if not user_data.empty:
                    st.table(user_data)
                else:
                    st.info("خزنتك فارغة، ابدأ بإضافة أول ذكرى.")
            else:
                st.sidebar.error("خطأ في الاسم أو كلمة المرور")

if __name__ == '__main__':
    main()
