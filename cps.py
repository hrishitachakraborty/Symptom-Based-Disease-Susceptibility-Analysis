import os
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk

def seir_model(S, E, I, R, beta, sigma, gamma, N, dt):
    dS_dt = -beta * S * I / N
    dE_dt = beta * S * I / N - sigma * E
    dI_dt = sigma * E - gamma * I
    dR_dt = gamma * I

    S_new = S + dS_dt * dt
    E_new = E + dE_dt * dt
    I_new = I + dI_dt * dt
    R_new = R + dR_dt * dt

    return S_new, E_new, I_new, R_new

class simulationAgent:
    def __init__(self, location, state='S'):
        self.location = location
        self.state = state  # 'S', 'E', 'I', 'R'

    def move(self):
        self.location = (self.location[0] + np.random.randint(-1, 2),
                         self.location[1] + np.random.randint(-1, 2))

    def interact(self, other_agent):
        pass  # This can be implemented further if needed

diseases_symptoms = {
    'COVID-19': ['fever', 'cough', 'fatigue', 'difficulty breathing', 'loss of smell/taste'],
    'Flu': ['fever', 'cough', 'body ache', 'sore throat', 'muscle aches', 'fatigue'],
    'Dengue': ['fever', 'rash', 'joint pain', 'headache', 'muscle pain', 'nausea'],
    'Common Cold': ['sneezing', 'runny nose', 'sore throat', 'congestion', 'cough'],
    'Malaria': ['fever', 'chills', 'headache', 'muscle pain', 'vomiting', 'diarrhea'],
    'Typhoid': ['fever', 'weakness', 'stomach pain', 'headache', 'loss of appetite'],
    'Tuberculosis': ['cough (lasting weeks)', 'weight loss', 'fatigue', 'fever', 'night sweats'],
    'Chikungunya': ['fever', 'joint pain', 'rash', 'muscle pain', 'headache'],
    'Pneumonia': ['cough', 'fever', 'chest pain', 'shortness of breath'],
    'Measles': ['fever', 'rash', 'runny nose', 'cough', 'red eyes'],
    'Chickenpox': ['fever', 'rash', 'tiredness', 'headache'],
    'Mumps': ['swollen glands', 'fever', 'headache', 'muscle aches'],
    'HIV/AIDS': ['fever', 'fatigue', 'weight loss', 'frequent infections', 'night sweats'],
    'Hepatitis A/B/C': ['fatigue', 'nausea', 'dark urine', 'jaundice (yellow skin/eyes)'],
    'Zika Virus': ['fever', 'rash', 'joint pain', 'red eyes', 'headache'],
    'Ebola': ['fever', 'vomiting', 'diarrhea', 'rash', 'bleeding', 'muscle pain'],
    'Meningitis': ['fever', 'headache', 'stiff neck', 'nausea', 'sensitivity to light'],
    'Lyme Disease': ['fever', 'headache', 'fatigue', 'joint pain', 'rash'],
    'Scarlet Fever': ['sore throat', 'rash', 'fever', 'red tongue', 'swollen glands'],
    'Bronchitis': ['cough (with mucus)', 'fatigue', 'shortness of breath', 'chest discomfort'],
    'RSV (Respiratory Syncytial Virus)': ['runny nose', 'coughing', 'wheezing', 'fever', 'difficulty breathing'],
    'Whooping Cough': ['severe coughing fits', 'runny nose', 'mild fever']
}

def match_symptoms(input_symptoms):
    possible_diseases = []
    for disease, symptoms in diseases_symptoms.items():
        match = len(set(input_symptoms) & set(symptoms)) / len(symptoms)
        if match > 0.49:  # Adjusted threshold for similarity
            possible_diseases.append(disease)
    return possible_diseases

def load_dataset(file_path):
    return pd.read_csv(file_path)

def run_simulation(symptoms, location, result_text):
    dataset = load_dataset('updated_epidemic_dataset.csv')
    probable_diseases = match_symptoms(symptoms)
    if not probable_diseases:
        result_text.set("No matching diseases found for the given symptoms.")
        return

    result = f"Likely diseases: {probable_diseases}\n\n"
    for disease in probable_diseases:
        filtered_data = dataset[(dataset['Disease'].astype(str) == disease) & (dataset['Location'].astype(str) == location)]

        if not filtered_data.empty:
            try:
                S = filtered_data['Susceptible (S)'].values[0]
                E = filtered_data['Exposed (E)'].values[0]
                I = filtered_data['Infective (I)'].values[0]
                R = filtered_data['Recovered (R)'].values[0]
                N = S + E + I + R

                beta = 0.3  # Infection rate
                sigma = 0.1  # Rate of exposed individuals becoming infectious
                gamma = 0.1  # Recovery rate
                dt = 1  # Time step

                for _ in range(10):  # Simulate for 10 time steps
                    S, E, I, R = seir_model(S, E, I, R, beta, sigma, gamma, N, dt)

            except IndexError as e:
                result += f"Error accessing values for {disease}: {e}\n"
            except Exception as e:
                result += f"Unexpected error for {disease}: {e}\n"

            susceptibility_percentage = (S / N) * 100
            result += f"Susceptibility for {disease}: {susceptibility_percentage:.2f}%\n\n"
        else:
            result += f"No data available for disease '{disease}' in location '{location}'.\n\n"
    
    result_text.set(result)

def submit(symptom_vars, location_combobox, result_text):
    selected_symptoms = [symptom for symptom, var in symptom_vars.items() if var.get()]
    location = location_combobox.get()
    run_simulation(selected_symptoms, location, result_text)

# Create the GUI
root = tk.Tk()
root.title("Disease Symptom Checker")
root.geometry("600x500")  # Set the window size

# Top label
tk.Label(root, text="Disease Symptom Checker", font=("Arial", 16)).pack(pady=10)

# Frame for the symptom checkboxes
symptom_frame = tk.Frame(root)
symptom_frame.pack(pady=10)

# Scrollable list of symptoms
canvas = tk.Canvas(symptom_frame, height=150)
scrollbar = tk.Scrollbar(symptom_frame, orient=tk.VERTICAL, command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Dictionary to hold symptom variables
symptom_vars = {}

# Create checkboxes for each symptom
for disease_symptoms in diseases_symptoms.values():
    for symptom in disease_symptoms:
        if symptom not in symptom_vars:  # Avoid duplicate symptoms
            var = tk.BooleanVar()
            symptom_vars[symptom] = var
            tk.Checkbutton(scrollable_frame, text=symptom, variable=var).pack(anchor="w")

# Location selection
tk.Label(root, text="Select your location:").pack(pady=5)
locations = ["Anna Nagar", "T Nagar", "Velachery", "Porur", "Guindy", "Adyar"]
location_combobox = ttk.Combobox(root, values=locations)
location_combobox.pack()

# Submit button
submit_button = tk.Button(root, text="Submit", command=lambda: submit(symptom_vars, location_combobox, result_text))
submit_button.pack(pady=10)

# Textbox to display results
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left", wraplength=500, bg="white", anchor="nw")
result_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
