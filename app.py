import os
import sys

import streamlit as st


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from rag import EcommerceRAG


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="E-Commerce AI Chatbot",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .product-card {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛒 E-Commerce AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Find products, get recommendations, and compare products using AI.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛍️ Shopping Assistant")

    st.write(
        """
        You can ask questions such as:

        • Find laptops under ₹60,000  
        • Recommend a phone  
        • Compare two products  
        • Which product has the highest rating?  
        • Show me headphones  
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# LOAD RAG SYSTEM
# ============================================================

@st.cache_resource
def load_rag():

    return EcommerceRAG()


try:

    rag = load_rag()

except Exception as e:

    st.error(
        "❌ Failed to initialize the AI system."
    )

    st.code(str(e))

    st.info(
        "Check your .env file and GEMINI_API_KEY."
    )

    st.stop()


# ============================================================
# CHAT MEMORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        # Display products if stored
        if (
            message["role"] == "assistant"
            and "products" in message
        ):

            products = message["products"]

            if products:

                with st.expander(
                    "🔎 Products considered"
                ):

                    for product in products:

                        st.markdown(
                            f"""
                            **{product['name']}**

                            🏷️ Brand: {product['brand']}  
                            💰 Price: ₹{product['price']}  
                            ⭐ Rating: {product['rating']}  
                            📦 Stock: {product['stock']}
                            """
                        )

                        st.divider()


# ============================================================
# USER INPUT
# ============================================================

user_input = st.chat_input(
    "Ask me about products..."
)


if user_input:

    # --------------------------------------------------------
    # Store user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_input)


    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "🔎 Searching products..."
            ):

                answer, products = rag.chat(
                    user_input
                )


            # ------------------------------------------------
            # Display answer
            # ------------------------------------------------

            st.markdown(answer)


            # ------------------------------------------------
            # Display retrieved products
            # ------------------------------------------------

            if products:

                with st.expander(
                    "🔎 Products considered"
                ):

                    for product in products:

                        st.markdown(
                            f"""
                            **{product['name']}**

                            🏷️ Brand: {product['brand']}  
                            💰 Price: ₹{product['price']}  
                            ⭐ Rating: {product['rating']}  
                            📦 Stock: {product['stock']}
                            """
                        )

                        st.divider()


            # ------------------------------------------------
            # Save assistant message
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "products": products
                }
            )


        except Exception as e:

            error_message = (
                "Sorry, I couldn't process your request."
            )

            st.error(error_message)

            with st.expander(
                "Technical details"
            ):

                st.code(str(e))

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🛒 E-Commerce AI Assistant • "
    "Powered by FAISS + Sentence Transformers + Gemini"
)