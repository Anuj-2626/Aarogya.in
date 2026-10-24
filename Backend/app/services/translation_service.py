from ..languages import validate_language


QUESTION_TRANSLATIONS = {
    "hi": {
        "CC_MAIN": "आज आपको अस्पताल आने का मुख्य कारण या समस्या क्या है?",
        "HPI_ONSET": "यह समस्या या लक्षण पहली बार कब शुरू हुआ?",
        "HPI_DURATION": "आपको यह समस्या कितने समय से हो रही है?",
        "HPI_LOCATION": "आपको यह समस्या या लक्षण ठीक कहाँ महसूस होता है?",
        "HPI_CHARACTER": "आप इस लक्षण का वर्णन कैसे करेंगे?",
        "HPI_SEVERITY": "0 से 10 के पैमाने पर यह लक्षण कितना गंभीर है?",
        "HPI_AGGRAVATING": "क्या कोई ऐसी चीज़ है जिससे यह लक्षण बढ़ जाता है?",
        "HPI_RELIEVING": "क्या कोई ऐसी चीज़ है जिससे यह लक्षण कम होता है या राहत मिलती है?",
        "HPI_ASSOCIATED": "क्या इस समस्या के साथ आपको कोई अन्य लक्षण भी हो रहे हैं?",
        "PMH_DISEASES": "क्या आपको कभी किसी बड़ी बीमारी या स्वास्थ्य समस्या का निदान हुआ है?",
        "PMH_SURGERY": "क्या आपकी कभी कोई बड़ी सर्जरी हुई है या आपको अस्पताल में भर्ती होना पड़ा है?",
        "MED_CURRENT": "क्या आप अभी कोई दवाइयाँ ले रहे हैं?",
        "MED_DETAILS": "यदि आपको पता हो, तो कृपया उन दवाइयों के नाम बताएं जो आप अभी ले रहे हैं।",
        "ALLERGY": "क्या आपको किसी दवा, भोजन या किसी अन्य चीज़ से कोई ज्ञात एलर्जी है?",
        "ALLERGY_DETAILS": "कृपया अपनी ज्ञात एलर्जी और उनसे होने वाली प्रतिक्रिया के बारे में बताएं।",
        "FAMILY_HISTORY": "क्या आपके करीबी परिवार में किसी को कोई बड़ी बीमारी या स्वास्थ्य समस्या है?",
        "PERSONAL_SMOKING": "क्या आप धूम्रपान करते हैं या तंबाकू का उपयोग करते हैं?",
        "PERSONAL_ALCOHOL": "क्या आप शराब का सेवन करते हैं?",
        "PERSONAL_OCCUPATION": "आपका व्यवसाय या सामान्य रूप से किस प्रकार का काम है?",
        "INVESTIGATIONS": "क्या आपने इस समस्या से संबंधित पहले कोई मेडिकल टेस्ट या जाँच करवाई है?",
        "PREVIOUS_TREATMENT": "क्या आपने इस समस्या के लिए पहले कोई उपचार लिया है?",
        "AYUSH_USE": "क्या आपने इस समस्या के लिए कोई आयुर्वेदिक, पारंपरिक या अन्य AYUSH उपचार लिया है?",
        "AYUSH_DETAILS": "कृपया आपके द्वारा लिए गए AYUSH या आयुर्वेदिक उपचार के बारे में बताएं।",
        "RED_FLAG_CHEST": "क्या आपको अभी सीने में तेज दर्द या दबाव महसूस हो रहा है?",
        "RED_FLAG_BREATHING": "क्या आपको अभी साँस लेने में बहुत कठिनाई हो रही है?",
        "RED_FLAG_CONSCIOUSNESS": "क्या हाल ही में आप बेहोश हुए हैं, आपकी चेतना चली गई थी या आप असामान्य रूप से भ्रमित हुए हैं?",
    },

    "mr": {
        "CC_MAIN": "आज तुम्हाला रुग्णालयात येण्याचे मुख्य कारण किंवा समस्या काय आहे?",
        "HPI_ONSET": "ही समस्या किंवा लक्षण पहिल्यांदा कधी सुरू झाले?",
        "HPI_DURATION": "तुम्हाला ही समस्या किती काळापासून आहे?",
        "HPI_LOCATION": "तुम्हाला ही समस्या किंवा लक्षण नेमके कुठे जाणवते?",
        "HPI_CHARACTER": "तुम्ही या लक्षणाचे वर्णन कसे कराल?",
        "HPI_SEVERITY": "0 ते 10 या प्रमाणात हे लक्षण किती तीव्र आहे?",
        "HPI_AGGRAVATING": "अशा कोणत्या गोष्टी आहेत ज्यामुळे हे लक्षण वाढते?",
        "HPI_RELIEVING": "अशा कोणत्या गोष्टी आहेत ज्यामुळे हे लक्षण कमी होते किंवा आराम मिळतो?",
        "HPI_ASSOCIATED": "या समस्येसोबत तुम्हाला इतर कोणती लक्षणेही जाणवत आहेत का?",
        "PMH_DISEASES": "तुम्हाला यापूर्वी कोणत्याही मोठ्या आजाराचे किंवा आरोग्य समस्येचे निदान झाले आहे का?",
        "PMH_SURGERY": "तुमची यापूर्वी कोणतीही मोठी शस्त्रक्रिया झाली आहे का किंवा तुम्हाला रुग्णालयात दाखल करण्यात आले आहे का?",
        "MED_CURRENT": "तुम्ही सध्या कोणतीही औषधे घेत आहात का?",
        "MED_DETAILS": "तुम्हाला माहिती असल्यास, तुम्ही सध्या घेत असलेल्या औषधांची नावे कृपया सांगा.",
        "ALLERGY": "तुम्हाला कोणत्याही औषधाची, अन्नाची किंवा इतर कोणत्याही गोष्टीची ज्ञात ऍलर्जी आहे का?",
        "ALLERGY_DETAILS": "कृपया तुमच्या ज्ञात ऍलर्जी आणि त्यांच्यामुळे होणाऱ्या प्रतिक्रियेबद्दल सांगा.",
        "FAMILY_HISTORY": "तुमच्या जवळच्या कुटुंबातील कोणाला मोठा आजार किंवा आरोग्य समस्या आहे का?",
        "PERSONAL_SMOKING": "तुम्ही धूम्रपान करता किंवा तंबाखूजन्य पदार्थ वापरता का?",
        "PERSONAL_ALCOHOL": "तुम्ही दारूचे सेवन करता का?",
        "PERSONAL_OCCUPATION": "तुमचा व्यवसाय किंवा नेहमीचे काम कोणत्या प्रकारचे आहे?",
        "INVESTIGATIONS": "या समस्येशी संबंधित तुम्ही यापूर्वी कोणतीही वैद्यकीय चाचणी किंवा तपासणी केली आहे का?",
        "PREVIOUS_TREATMENT": "या समस्येसाठी तुम्ही यापूर्वी कोणतेही उपचार घेतले आहेत का?",
        "AYUSH_USE": "या समस्येसाठी तुम्ही कोणतेही आयुर्वेदिक, पारंपरिक किंवा इतर AYUSH उपचार घेतले आहेत का?",
        "AYUSH_DETAILS": "तुम्ही घेतलेल्या AYUSH किंवा आयुर्वेदिक उपचारांबद्दल कृपया सांगा.",
        "RED_FLAG_CHEST": "तुम्हाला सध्या छातीत तीव्र वेदना किंवा दाब जाणवत आहे का?",
        "RED_FLAG_BREATHING": "तुम्हाला सध्या श्वास घेण्यास खूप त्रास होत आहे का?",
        "RED_FLAG_CONSCIOUSNESS": "तुम्ही अलीकडे बेशुद्ध पडला आहात, शुद्ध हरपली आहे किंवा असामान्यपणे गोंधळलेले वाटले आहे का?",
    },
}


class TranslationService:
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        validate_language(source_language)
        validate_language(target_language)

        if not text or not text.strip():
            raise ValueError(
                "Text to translate cannot be empty"
            )

        if source_language == target_language:
            return text

        raise NotImplementedError(
            "Translation provider is not configured yet"
        )

    def translate_question(
        self,
        question_text: str,
        source_language: str,
        target_language: str,
        question_code: str | None = None
    ) -> str:
        validate_language(source_language)
        validate_language(target_language)

        if not question_text or not question_text.strip():
            raise ValueError(
                "Question text cannot be empty"
            )

        if source_language == target_language:
            return question_text

        if source_language != "en":
            raise ValueError(
                "Question translations currently use English "
                "as the source language"
            )

        if target_language == "en":
            return question_text

        if question_code is None:
            raise ValueError(
                "Question code is required for localized "
                "clinical questions"
            )

        language_translations = QUESTION_TRANSLATIONS.get(
            target_language
        )

        if language_translations is None:
            raise ValueError(
                f"No question translations available for "
                f"language: {target_language}"
            )

        translated_question = language_translations.get(
            question_code
        )

        if translated_question is None:
            raise ValueError(
                f"No translation available for question: "
                f"{question_code}"
            )

        return translated_question


translation_service = TranslationService()
