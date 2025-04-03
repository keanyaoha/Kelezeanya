import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
print("Libraries Loaded Successfully")

# Load datasets
def load_emission_factors():
    csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
    return pd.read_csv(csv_url)

def load_per_capita_data():
    return pd.read_csv("per_capita_filtered.csv")

emission_factors = load_emission_factors()
per_capita_data = load_per_capita_data()
print("Datasets Loaded Successfully")

# Extract country lists
emission_countries = emission_factors.columns[1:].tolist()
per_capita_countries = per_capita_data["Country"].unique().tolist()

# Common countries
common_countries = set(emission_countries).intersection(set(per_capita_countries))

# Streamlit UI
st.title("Carbon Footprint Per Capita")
st.image('carbon_image.jpg')

# Collect identity and mood
identity = st.text_input("Type your Champ:")
mood = st.selectbox("Select your mood:", ["is Happy", "is slightly Happy"])

if not identity or not mood:
    st.warning("Please enter your identity and select your mood before proceeding.")
else:
    st.write(f"Welcome {identity}! Let's calculate your Carbon Footprint.")

# Country selection
selected_country = st.selectbox("Select a country:", sorted(set(emission_countries + per_capita_countries)))

if selected_country:
    if selected_country not in emission_countries and selected_country not in per_capita_countries:
        st.warning(f"{selected_country} not found in both datasets.")
    else:
        # Fetch per capita CO2 data
        country_per_capita = per_capita_data.loc[per_capita_data["Country"] == selected_country, "PerCapitaCO2"].values
        eu_27_per_capita = per_capita_data.loc[per_capita_data["Country"] == "European Union (27)", "PerCapitaCO2"].values
        world_per_capita = per_capita_data.loc[per_capita_data["Country"] == "World", "PerCapitaCO2"].values

        country_per_capita = country_per_capita[0] if len(country_per_capita) > 0 else None
        eu_27_per_capita = eu_27_per_capita[0] if len(eu_27_per_capita) > 0 else None
        world_per_capita = world_per_capita[0] if len(world_per_capita) > 0 else None

        # Fetch emission factors data
        if selected_country in emission_countries:
            activities = emission_factors['Activity'].tolist()

            if "current_activity_start" not in st.session_state:
                st.session_state.current_activity_start = 0
                st.session_state.emission_values = {}

            activities_per_page = 5
            activities_to_display = activities[st.session_state.current_activity_start: st.session_state.current_activity_start + activities_per_page]

            for activity in activities_to_display:
                activity_row = emission_factors[emission_factors['Activity'] == activity]
                factor = activity_row[selected_country].values[0] if not activity_row.empty else None
                if factor is not None:
                    user_input = st.number_input(
                        f"{activity.replace('_', ' ').capitalize()}", min_value=0, step=1, key=activity
                    )
                    st.session_state.emission_values[activity] = user_input * factor

            if st.session_state.current_activity_start + activities_per_page < len(activities):
                next_button = st.button("Next")
                if next_button:
                    st.session_state.current_activity_start += activities_per_page

            if st.session_state.current_activity_start + activities_per_page >= len(activities):
                calculate_button = st.button("Calculate Carbon Footprint")
                if calculate_button:
                    total_emission = sum(st.session_state.emission_values.values())
                    
                    # Prepare bar chart
                    labels = ["Your Footprint", selected_country, "EU (27)", "World"]
                    values = [
                        total_emission,
                        country_per_capita if country_per_capita else 0,
                        eu_27_per_capita if eu_27_per_capita else 0,
                        world_per_capita if world_per_capita else 0
                    ]
                    
                    fig, ax = plt.subplots()
                    ax.bar(labels, values, color=['blue', 'green', 'orange', 'red'])
                    ax.set_ylabel("Per Capita Emission")
                    ax.set_title("Carbon Footprint Distribution")
                    st.pyplot(fig)

                    st.subheader(f"Your Carbon Footprint is: {total_emission:.4f}")
                    if country_per_capita is not None:
                        st.subheader(f"Per capita for {selected_country} is: {country_per_capita}")
                    if eu_27_per_capita is not None:
                        st.subheader(f"Per capita for European Union(27) is: {eu_27_per_capita}")
                    if world_per_capita is not None:
                        st.subheader(f"Per capita for World is: {world_per_capita}")
        else:
            st.warning(f"Emission factor data for {selected_country} is not available.")
print("Completed!")
