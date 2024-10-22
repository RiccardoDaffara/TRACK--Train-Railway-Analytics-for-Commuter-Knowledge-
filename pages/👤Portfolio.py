import streamlit as st
import base64

# Setting up the page title and icon
st.set_page_config(page_title="Riccardo Daffara Portfolio", page_icon=":trophy:", layout="wide")


# Header Section
def header():
    st.title("👋 Welcome to My Portfolio")
    st.subheader("Master's Student in Data Science & AI | Efrei")
    st.write("""
    Hi! I'm Riccardo Daffara, and I'm currently pursuing a Master's degree in Data Science and Artificial Intelligence at **Efrei**. 
    I am passionate about machine learning, data analytics, and building AI solutions to solve real-world problems. 
    This portfolio highlights some of my projects, skills, and achievements.
    """)

    # Load and display profile picture
    with open("pages/pp.png", "rb") as file:
        img_data = file.read()

    # Encodage de l'image en base64 pour pouvoir l'injecter dans du HTML
    img_base64 = base64.b64encode(img_data).decode()

    st.markdown(
        f"""
        <style>
        .img-circle {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 200px; /* Taille de l'image */
            height: 200px;
            border-radius: 50%;
            object-fit: cover;
        }}
        </style>
        <img src="data:image/jpeg;base64,{img_base64}" class="img-circle">
        """,
        unsafe_allow_html=True
    )

    # Adding the CV download button
    st.markdown("<h3 style='text-align: center;'>Riccardo DAFFARA</h3>", unsafe_allow_html=True)
    with open("pages/CV_DAFFARA_1024.pdf", "rb") as cv_file:  # Replace with your actual CV file path
        cv_data = cv_file.read()
        st.download_button(
            label="📄 Download CV",
            data=cv_data,
            file_name="Riccardo_Daffara_CV.pdf",  # The name of the downloaded file
            mime="application/pdf"
        )


# About Me Section
def about_me():
    st.header("About Me")
    st.write("""
    I have a strong interest in machine learning, deep learning, and computer vision. 
    Through various projects, I have honed my skills in **Python**, **TensorFlow**, **Pandas**, **Scikit-learn**, and other essential libraries for data science.

    I enjoy collaborating with others on innovative tech projects. 
    Here are some quick details about me:
    - 🎓 **Education**: Master 1 in Data Science and AI at Efrei
    - 💻 **Skills**: Python, Machine Learning, Deep Learning, Data Analysis, NLP
    - 📫 **Email**: riccardo.daffara@efrei.net
    """)


# Projects Section
def projects():
    st.header("My Projects")

    st.subheader("1. Evaluating different models for Machine Learning on a diabetes dataset")
    st.write("""
    In this project, I compared different ML models like **Linear Regression**, **Random Forest**, **Decision Trees** and **MLP** on a diabetes dataset. By analyzing the different metrics given with **Scikit-Learn** library I could identify the better model.
    """)

    st.subheader("2. MindBloom")
    st.write("""
    I have participated in the development of the MindBloom prototype app. The goal is to give users more information about their concentration and how their mind and memorization works. By doing different tests on the app they can have a personalized profile to see their good points and the one they have to work on.
    """)

    st.subheader("3. EMISI Project")
    st.write("""
    In a team of 5, I've studied the impact of a weightless atmosphere on the microbiota of the human gut system. We've participated in the 65th parabolic flight campaign in Bordeaux. Our project was selected by the CNES.
    """)


# Skills Section
def skills():
    st.header("Skills")
    skill_columns = st.columns(3)

    with skill_columns[0]:
        st.write("### Programming Languages")
        st.write("""
        - Python
        - SQL
        - C
        - Java
        """)

    with skill_columns[1]:
        st.write("### Libraries & Tools")
        st.write("""
        - TensorFlow
        - Scikit-learn
        - Pandas & NumPy
        - Matplotlib & Seaborn
        """)

    with skill_columns[2]:
        st.write("### Technologies")
        st.write("""
        - Machine Learning
        - Deep Learning
        - Natural Language Processing
        - Data Visualization
        - Bio-informatics
        """)


# Contact Section
def contact():
    st.header("Contact Me")
    st.write("""
    Feel free to reach out to me on:

    - 📧 Email: riccardo.daffara@efrei.net
    - 💼 LinkedIn: [linkedin.com/in/riccardo-daffara](https://www.linkedin.com/in/riccardo-daffara/)
    - 🐱 GitHub: [github.com/RiccardoDaffara](https://github.com/RiccardoDaffara)
    """)


# Main function to call sections
def main():
    header()
    about_me()
    projects()
    skills()
    contact()


if __name__ == "__main__":
    main()
