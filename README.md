# BizCardX-Extracting-Business-Card-Data-with-OCR

## Project Overview
BizCardX is a user-friendly tool for extracting information from business cards. The tool uses OCR technology to recognize text on business cards and extracts the data into a SQL database after classification using regular expressions. Users can access the extracted information using a GUI built using streamlit. The BizCardX application is a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information. The extracted information would be displayed in a clean and organized manner, and users would be able to easily add it to the database with the click of a button. Further the data stored in database can be easily Read, updated and deleted by user as per the requirement.

## Libraries/Modules used for the project!
* Pandas - (To Create a DataFrame with the scraped data)
* mysql.connector - (To store and retrieve the data)
* EasyOCR - (To extract text from images)
* Streamlit - (To Create Graphical user Interface)

## Workflow
* Execute the “BizCardX_main.py” using the streamlit run command.
* A webpage is displayed in browser, I have created the app with four menu options namely HOME, UPLOAD & EXTRACT, MODIFY & DELETE where user has the option to upload the respective Business Card whose information has to be extracted, stored, modified or deleted if needed.
* Once user uploads a business card, the text present in the card is extracted by easyocr library.
* On Clicking Update in DB Button the data gets stored in the MySQL Database.
* With the help of MODIFY menu the uploaded data’s in SQL Database can be accessed to View and Update Operations.
* Further with the help of DELETE menu the uploaded data’s in SQL Database can be deleted.
