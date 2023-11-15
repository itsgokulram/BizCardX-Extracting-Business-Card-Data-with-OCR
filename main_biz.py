import cv2
import os
import re
import easyocr
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
from PIL import Image
import matplotlib.pyplot as plt

#setting page config

st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR | by Gokul Ram",
                   layout = "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *Gokul Ram*!"""})

st.markdown("<h1 style='text-align: center; color: grey;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)
# st.markdown("<h2 style='text-align: right; color: grey;'>by Gokul Ram</h2>", unsafe_allow_html=True)

#creating option menu

selected = option_menu(None, ["Home", "Upload & Extract", "Modify data", "Delete"],
                       icons = ["house", "cloud-upload", "pencil-square", "trash"],
                       default_index = 0,
                       orientation = "horizontal",
                       styles = {"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                                 "icon": {"font-size": "35px"},
                                 "container" : {"max-width": "6000px"},
                                 "nav-link-selected": {"background-color": "#6495ED"}})

# initializing the easyocr reader
reader = easyocr.Reader(['en'])

# initializing MYSQL connection

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database= "bizcardx"
)
# print(mydb)
mycursor = mydb.cursor(buffered=True)

# Table creation

mycursor.execute('''CREATE TABLE IF NOT EXISTS card_details
                 (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                 company_name TEXT,
                 card_holder TEXT,
                 designation TEXT,
                 contact_number VARCHAR(50),
                 email TEXT,
                 website TEXT,
                 area TEXT,
                 city TEXT,
                 state TEXT,
                 pincode VARCHAR(10)
                 )''')

#home menu

if selected == "Home":
    home_col1, home_col2, home_col3 = st.columns([5,1,3])

    with home_col1:
        st.markdown("## :green[**Technologies Used :**] Python, SQL, Pandas, Easy OCR, Streamlit")
        
        st.markdown("### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it \
                    using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information \
                    into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business \
                    card image and extracted information.")
    with home_col2:
        st.write(" ")

    with home_col3:
        st.image("/Users/gokul/My Apple/vs_code_practice/bizcard_project/bizcad.png")

# upload and extract menu

if selected == "Upload & Extract":

    st.markdown("### Upload a Business card")
    uploaded_card = st.file_uploader("upload here", label_visibility = "collapsed", type = ["png", "jpg", "jpeg"])

    if uploaded_card is not None:

        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())

        save_card(uploaded_card)  #calling the save function
    
    #displaying the uploaded card
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("### Preview of the uploaded card")
            st.image(uploaded_card)

        # easyOCR
        # /Users/gokul/My Apple/vs_code_practice/bizcard_project/uploaded_cards
        saved_image = os.getcwd()+ "/" + "uploaded_cards" + "/" + uploaded_card.name
        result = reader.readtext(saved_image, detail= 0, paragraph= False)

        data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "contact_number" : [],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pincode" : []
                }
        
        def get_data(res):

            for ind, i in enumerate(res):

                # Company name
                if ind == len(res)-1:
                    data["company_name"].append(i)

                # Card holder name
                elif ind == 0:
                    data["card_holder"].append(i)

                # Designation
                elif ind == 1:
                    data["designation"].append(i)

                # Contact number
                elif "-" in i:
                    data["contact_number"].append(i)
                    if len(data["contact_number"]) ==2:
                        data["contact_number"] = " & ".join(data["contact_number"])
                
                # E-mail ID
                elif "@" in i:
                    data["email"].append(i)

                # Website
                elif "www" in i.lower() or "www." in i.lower():
                    data["website"].append(i)

                # Area
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                # City name
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # State
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)

                if state_match:
                        data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                # pincode
                if len(i)>=6 and i.isdigit():
                    data["pincode"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pincode"].append(i[10:])
        
        get_data(result)

        # to create dataframe
        def create_df(data):
            df = pd.DataFrame(data)
            return df

        df = create_df(data)
        st.success("### Data Extracted")
        st.write(df)

        if st.button("Upload to Database"):

            for i, row in df.iterrows():

                query = """INSERT INTO card_details(company_name, card_holder, designation, contact_number, email, website, area, city, state, pincode)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                mycursor.execute(query, tuple(row))
                mydb.commit()
            
            st.success("Uploaded to database successfully")


# Delete menu

if selected == "Delete":
    
    del_col1, del_col2 = st.columns([7,3])

    try:
        with del_col1:
            st.markdown("### Delete data from database")
            st.write("   ")

            mycursor.execute("SELECT card_holder FROM card_details")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            
            selected_card = st.selectbox("Select a card holder name to delete", list(business_cards.keys()))
            st.write(f"### You have selected :red[**{selected_card}'s**] card to delete")
            st.write("   ")

            if st.button("Delete selected card"):
                mycursor.execute(f"DELETE FROM card_details WHERE card_holder = '{selected_card}'")
                mydb.commit()
                st.success("Deleted from database successfully")

        with del_col2:
            st.write("   ")
    
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("SELECT company_name, card_holder, designation, contact_number, email, website, area, city, state, pincode FROM card_details")
        updated_df = pd.DataFrame(mycursor.fetchall(), columns = ["Company_Name","Card_Holder","Designation","Contact_Number","Email","Website","Area","City","State","Pincode"])
        st.write(updated_df)