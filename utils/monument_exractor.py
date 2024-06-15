def extract_monument_name(model, img_path):
    monuments = {}
    monument_english  = ['Old Medina','Bab Chellah','Bab Rouah','Dome des Almoravides','Eglise du Sacré-Cœur','Koutoubia', 'The Saadian Tombs', 'Mausoleum of Mohammed V', 'Hassan II Mosque', 'Palace of the Bahia', 'Hassan Tower', 'Yves Saint Laurent', 'Jamaa El Fna', 'Menara', 'Oudaya']
    monuments = dict(zip(model.names.values(), monument_english))
    result = model.predict(img_path)
    result_class =  model.names[int(result[0].boxes[0].cls)]
    # print("Result class : ", monuments[result_class])
    return monuments[result_class]