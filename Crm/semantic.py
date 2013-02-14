# -*- coding: utf-8 -*-

import codecs
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
import xlwt

#dbpedia = SPARQLWrapper("http://dbpedia.org/sparql")

def get_french_cities(source):
    sparql = SPARQLWrapper(source)
    
    query = u"""
        PREFIX dbpp:<http://fr.dbpedia.org/property/>
        PREFIX dbpo:<http://dbpedia.org/ontology/>
        PREFIX dbpr:<http://fr.dbpedia.org/resource/>
        SELECT ?city ?departement ?region ?zipcode
        WHERE {
            ?c rdf:type dbpedia-owl:PopulatedPlace .
            ?c dbpedia-owl:department ?d .
            ?c dbpedia-owl:region ?r .
            ?c rdfs:label ?city .
            ?d rdfs:label ?departement .
            ?r rdfs:label ?region .
            ?c dbpedia-owl:postalCode ?zipcode .
        }
    """
    #"""
    #    LIMIT 500
    #"""
    #?city dbpedia-owl:country dbpedia:France .
    #?city dbpedia-owl:department ?departement .
    #?city dbpedia-owl:region ?region .
    #?departement dbpprop:name ?dep_name .
    #        ?region dbpprop:name ?region_name .
    #SELECT ?city_name ?dep_name ?region_name
            
    
    #query = """
    #    SELECT ?name
    #    WHERE {
    #        ?c rdfs:label ?name
    #        ?c dbpprop:wikiPageUsesTemplate <http://dbpedia.org/resource/Template:Infobox_settlement> . 
    #        ?c dbpedia-owl:country <http://dbpedia.org/resource/Country> .
    #        FILTER ( lang(?name) = "fr" && ?population > 5000)
    #    }
    #"""
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()["results"]["bindings"]
        data = []
        for json_data in results:
            data.append(dict([(k, v["value"]) for (k, v) in json_data.items()]))    
        return data
    except SPARQLExceptions.QueryBadFormed, msg:
        print "Error: ", msg

def dump_xls(cities_list):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("villes")
    
    for line, city in enumerate(cities_list):
        for col, field in enumerate(['city', 'zipcode', 'departement', 'region']):
            ws.write(line, col, city[field])
    
    wb.save('villes.xls')
    
if __name__ == "__main__":
    cities_list = get_french_cities("http://fr.dbpedia.org/sparql")
    dump_xls(cities_list)
    #for d in cities_list:
    #    print "*********************************"
    #    for k in d:
    #        print k, d[k].encode('unicode_escape')
    ##print get_french_cities("http://fr.dbpedia.org/sparql")#.encode('unicode_escape')