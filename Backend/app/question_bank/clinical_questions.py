CLINICAL_QUESTIONS = [
    {
        "question_code": "CC_MAIN",
        "question_text": "What is the main problem or symptom that brought you to the hospital today?",
        "question_type": "text",
        "history_section": "chief_complaint",
        "sequence": 1,
        "required": True,
        "parent_question": None
    },
    {
        "question_code": "HPI_ONSET",
        "question_text": "When did this problem or symptom first begin?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 2,
        "required": True,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_DURATION",
        "question_text": "How long have you been experiencing this problem?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 3,
        "required": True,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_LOCATION",
        "question_text": "Where exactly do you feel the problem or symptom?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 4,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_CHARACTER",
        "question_text": "How would you describe the symptom?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 5,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_SEVERITY",
        "question_text": "How severe is the symptom on a scale from 0 to 10?",
        "question_type": "number",
        "history_section": "history_of_present_illness",
        "sequence": 6,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_AGGRAVATING",
        "question_text": "Does anything make the symptom worse?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 7,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_RELIEVING",
        "question_text": "Does anything make the symptom better or provide relief?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 8,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "HPI_ASSOCIATED",
        "question_text": "Are you experiencing any other symptoms along with this problem?",
        "question_type": "text",
        "history_section": "history_of_present_illness",
        "sequence": 9,
        "required": False,
        "parent_question": "CC_MAIN"
    },
    {
        "question_code": "PMH_DISEASES",
        "question_text": "Have you ever been diagnosed with any major medical conditions?",
        "question_type": "text",
        "history_section": "past_medical_history",
        "sequence": 10,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "PMH_SURGERY",
        "question_text": "Have you ever had any major surgery or been hospitalized?",
        "question_type": "text",
        "history_section": "past_medical_history",
        "sequence": 11,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "MED_CURRENT",
        "question_text": "Are you currently taking any medicines?",
        "question_type": "yes_no",
        "history_section": "medication_history",
        "sequence": 12,
        "required": True,
        "parent_question": None
    },
    {
        "question_code": "MED_DETAILS",
        "question_text": "Please tell us the names of the medicines you are currently taking, if you know them.",
        "question_type": "text",
        "history_section": "medication_history",
        "sequence": 13,
        "required": False,
        "parent_question": "MED_CURRENT"
    },
    {
        "question_code": "ALLERGY",
        "question_text": "Do you have any known medicine, food, or other allergies?",
        "question_type": "yes_no",
        "history_section": "allergy_history",
        "sequence": 14,
        "required": True,
        "parent_question": None
    },
    {
        "question_code": "ALLERGY_DETAILS",
        "question_text": "Please tell us about your known allergies and what reaction they cause.",
        "question_type": "text",
        "history_section": "allergy_history",
        "sequence": 15,
        "required": False,
        "parent_question": "ALLERGY"
    },
    {
        "question_code": "FAMILY_HISTORY",
        "question_text": "Does anyone in your close family have any major medical conditions?",
        "question_type": "text",
        "history_section": "family_history",
        "sequence": 16,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "PERSONAL_SMOKING",
        "question_text": "Do you smoke or use tobacco products?",
        "question_type": "yes_no",
        "history_section": "personal_social_history",
        "sequence": 17,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "PERSONAL_ALCOHOL",
        "question_text": "Do you consume alcohol?",
        "question_type": "yes_no",
        "history_section": "personal_social_history",
        "sequence": 18,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "PERSONAL_OCCUPATION",
        "question_text": "What is your occupation or usual type of work?",
        "question_type": "text",
        "history_section": "personal_social_history",
        "sequence": 19,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "INVESTIGATIONS",
        "question_text": "Have you had any medical tests or investigations related to this problem before?",
        "question_type": "text",
        "history_section": "previous_investigations",
        "sequence": 20,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "PREVIOUS_TREATMENT",
        "question_text": "Have you received any treatment for this problem before?",
        "question_type": "text",
        "history_section": "previous_treatment",
        "sequence": 21,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "AYUSH_USE",
        "question_text": "Have you used any Ayurvedic, traditional, or other AYUSH treatment for this problem?",
        "question_type": "yes_no",
        "history_section": "ayush_history",
        "sequence": 22,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "AYUSH_DETAILS",
        "question_text": "Please tell us about the AYUSH or Ayurvedic treatment you have used.",
        "question_type": "text",
        "history_section": "ayush_history",
        "sequence": 23,
        "required": False,
        "parent_question": "AYUSH_USE"
    },
    {
        "question_code": "RED_FLAG_CHEST",
        "question_text": "Are you currently experiencing severe chest pain or pressure?",
        "question_type": "yes_no",
        "history_section": "red_flags",
        "sequence": 24,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "RED_FLAG_BREATHING",
        "question_text": "Are you having severe difficulty breathing right now?",
        "question_type": "yes_no",
        "history_section": "red_flags",
        "sequence": 25,
        "required": False,
        "parent_question": None
    },
    {
        "question_code": "RED_FLAG_CONSCIOUSNESS",
        "question_text": "Have you recently fainted, lost consciousness, or become unusually confused?",
        "question_type": "yes_no",
        "history_section": "red_flags",
        "sequence": 26,
        "required": False,
        "parent_question": None
    }
]