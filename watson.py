import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, ConceptsOptions, EmotionOptions, RelationsOptions, SemanticRolesOptions, SentimentOptions, SyntaxOptions





def login():
  # Login to IBM
  authenticator = IAMAuthenticator('')
  natural_language_understanding = NaturalLanguageUnderstandingV1(
      version='2020-08-01',
      authenticator=authenticator)
  natural_language_understanding.set_service_url('')
  return natural_language_understanding
def analyzeText(client, text):
  # Analyze Text
  response = client.analyze(
      text=text,
      features=Features(
          entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
          keywords=KeywordsOptions(emotion=True, sentiment=True, limit=2),
          categories=CategoriesOptions(limit=100),
          concepts=ConceptsOptions(limit=100),
          emotion=EmotionOptions(),
          # emotion=EmotionOptions(targets=['apples','oranges'])
          relations=RelationsOptions(),
          semantic_roles=SemanticRolesOptions(keywords=True , entities=True),
          sentiment=SentimentOptions(),
          # sentiment=SentimentOptions(targets=['stocks']),
          syntax=SyntaxOptions(sentences=True),
          )
    ).get_result()
  return json.dumps(response, indent=2)





