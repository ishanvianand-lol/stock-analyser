import streamlit as st

def footer():
    footer_html = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}

      .main .block-container {
          padding-bottom: 80px; /* make more space for footer */
      }

      .custom-footer {
          font-family: 'Poppins', sans-serif;
          position: fixed;
          left: 0;
          bottom: 0px; 
          width: 100vw;
          background: rgba(0, 0, 0, 0.25);
          color: #f9f9f9;
          padding: 8px 0;
          font-size: 15px;
          font-weight: 500;
          backdrop-filter: blur(15px);
          z-index: 999;
          display: flex;
          justify-content: center;  /* center content horizontally */
          align-items: center;
      }

      .footer-content {
          display: flex;
          gap: 20px;
      }

      .footer-content a {
          color: #70a5ff;
          text-decoration: none;
          transition: color 0.3s ease;
      }

       .footer-content i {
          font-size: 20px; /* make icons bigger */
          vertical-align: middle;
          margin-right: 5px;
      }

      .footer-content a:hover {
          color: #ffffff;
      }
    </style>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <div class="custom-footer">
        <div class="footer-content">
            <b>Ishanvi Anand &copy; 2025</b>
            <a href="https://github.com/ishanvianand-lol" target="_blank"><i class="fab fa-github"></i> </a>
            <a href="https://www.linkedin.com/in/ishanvi-anand-a445a82b3" target="_blank"><i class="fab fa-linkedin"></i> </a>
        </div>
    </div>
    """

    st.markdown(footer_html, unsafe_allow_html=True)
