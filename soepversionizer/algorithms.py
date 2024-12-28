import pandas as pd
from soepversionizer.database import remove_version_suffix


def get_questions_with_same_item_name(questions, quest_expl, study, questionnaire, question):

    # Get items associated with a question
    associated_items = questions.loc[
        (questions['study']==study) & (questions['questionnaire']==questionnaire) & (questions['question']==question) 
        & questions['scale'].isin(['bin', 'cat', 'int', 'chr']),
        ['item', 'output']
    ].to_dict('records')

    search_items = []
    for i in associated_items:
        search_items += i['item'].split(',')
        search_items += i['output'].split(',')

    search_items = [remove_version_suffix(i) for i in search_items if i!=""]

    index = quest_expl.loc[(quest_expl['item'].isin(search_items)) | (quest_expl['output'].isin(search_items))].index
    index = index.drop_duplicates()
    
    matches = questions.loc[index, ['study', 'questionnaire', 'question']].to_dict('records')

    select = pd.Series(False, index=questions.index)
    for match in matches:
         select |= (questions['study']==match['study']) & (questions['questionnaire']==match['questionnaire']) & (questions['question']==match['question'])
     
    return questions[select]
