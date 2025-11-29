import streamlit as st

def footer():
    footer_html = """
    <style>
    /* Import Google Font */
      @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
      
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      
      /* Push content up to make room for footer */
      .main .block-container {
          padding-bottom: 50px;
      }

      .custom-footer {
          font-family: 'Poppins', sans-serif;
          position: fixed;
          left: 0;
          bottom: 0;
          width: 100vw;
          background: rgba(0, 0, 0, 0.25);
          color: #f9f9f9;
          padding: 8px 0;
          font-size: 15px;
          font-weight: 500;
          backdrop-filter: blur(15px);
          z-index: 999;
          margin-left: calc(-50vw + 50%);
      }
      
      .footer-content {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          max-width: 100%;
          padding: 0 40px;
          align-items: center;
      }

      .footer-left {
          text-align: left;
      }

      .footer-center {
          text-align: center;
      }

      .footer-right {
          text-align: right;
      }

      .footer-right a {
          margin-left: 15px;
          color: #70a5ff;
          text-decoration: none;
          transition: color 0.3s ease;
      }

      .footer-right a:hover {
          color: #ffffff;
      }
    </style>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <div class="custom-footer">
        <div class="footer-content">
            <div class="footer-left">
                 <b>Ishanvi Anand</b> &copy; 2025
            </div>
            <div class="footer-center">               
            </div>
            <div class="footer-right">
                <a href="https://github.com/ishanvianand-lol" target="_blank">
                    <i class="fab fa-github"></i> Github
                </a>
                <a href="https://www.linkedin.com/in/ishanvi-anand-a445a82b3" target="_blank">
                    <i class="fab fa-linkedin"></i> LinkedIn
                </a>
            </div>
        </div>
    </div>
    """

    st.markdown(footer_html, unsafe_allow_html=True)