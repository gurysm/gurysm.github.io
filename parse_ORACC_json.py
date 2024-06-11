def parse_ORACC_json(lemmatized_data_json, meta_data, dollar_keys):
    lemma_list = []
    for JSONobject in lemmatized_data_json['cdl']:
        if 'cdl' in JSONobject: 
            lemma_list.extend(parse_ORACC_json(JSONobject, meta_data, dollar_keys))
        if 'label' in JSONobject:
            meta_data['label'] = JSONobject['label']
        if 'f' in JSONobject:
            lemma = JSONobject['f']
            lemma['ftype'] = JSONobject.get('ftype')
            lemma['id_word'] = JSONobject['ref']
            lemma['label'] = meta_data['label']
            lemma['id_text'] = meta_data['id_text']
            lemma_list.append(lemma)
        if 'strict' in JSONobject and JSONobject['strict'] == '1':
            lemma = {key: JSONobject[key] for key in dollar_keys}
            lemma['id_word'] = JSONobject['ref']
            lemma['id_text'] = meta_data['id_text']
            lemma_list.append(lemma)
    return lemma_list