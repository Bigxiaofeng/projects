#!/usr/bin/env python

#Code to extract movies in a particular language and from a particular country
#Sameet Sreenivasan Aug 2014

#Primary function is: GET_ITEMS which takes arguments:
#chosenlanguage: String containing primary language of the film (examples: 'English','Danish' etc.)
#chosencountry: String containing the primary country that the film is associated with (examples: 'USA', 'Canada' etc.)
#outfilename: String with the name of the file where the output is written. output is in 3 column format that has the movie_id and the release month and year

#This function assumes that all items corresponding to movies have been obtained from the (local) SQL IMDb table 
#and are written to a file named "allmovies.txt". To do this create a directory (named in usr/local/:
# >mkdir imdbOutput
# >sudo chmod -R 777 imdbOutput
#Then a query of the form:
# >select id from title where kind_id = 1 into outfile '/usr/local/imdbOutput/allmovies.txt';

#To create an SQL Table with the IMDb data, follow instructions at: http://imdbpy.sourceforge.net/docs/README.sqldb.txt 


from imdb import IMDb  #the IMDbPy module is available here:http://imdbpy.sourceforge.net/

#g = open('outfiletest.txt','r')
def get_items(chosenlanguage,chosencountry,outfilename): 

    i = IMDb('sql',uri='mysql://root@localhost/imdb')
    g = open('/usr/local/allmovies.txt','r')
    
    #Convert month names to numbers, with 13 indicating absence of month when year is present
    monthno ={'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12,'NoMonth':13}
    
    num_movies = 0; #counter storing total number of movies written to outfile
    f = open(outfilename,'w')
    for line in g:
        m_id = line.rstrip('\n')
        print m_id
        m_obj = i.get_movie(m_id)
        print m_obj
        i.update(m_obj)
        
        #Evaluates condition that the item has the chosen language
        chosenlangpresent = False
        if m_obj.has_key('languages'):
            languagelist = m_obj['languages']
            if chosenlanguage in languagelist:
                chosenlangpresent = True
        
        #Evaluates condition that the item has the chosen country in country of origin
        chosencountrypresent = False
        if m_obj.has_key('countries'):
            countrylist = m_obj['countries']
            if chosencountry in countrylist[0]:  #Primary production company is in chosen country
                chosencountrypresent = True
                
        if chosencountrypresent and chosenlangpresent: # if all conditions for filtering are satisifed
            num_movies += 1
            # exract release dates in chosen country
            if m_obj.has_key('release dates'):
                rdlist = m_obj['release dates']
                rd = 'NULL'
                for item in rdlist:
                    if chosencountry in item:
                        rd = item.encode('ascii','ignore')
                        break
                if rd != 'NULL':    
                    if '::' in rd:
                        rd = rd.split('::')[0]
                    if ':' in rd: #date exists   
                        rd = rd.split(':')[1]
                        rd = rd.split(' ')
                        if len(rd) >= 2: #month and year exist
                            if rd[-2] in monthno:
                                month = monthno[rd[-2]]
                            else:
                                month = 13
                            year = int(rd[-1])
                        else:
                            month = 13
                            year = int(rd[0])
                    else:
                        month = 0
                        year = 0
                else:
                    month = 0
                    year =  0
                    
            else:
                month = 0
                year =  0
                            
            f.write(str(m_id)+'\t'+str(year)+'\t'+str(month)+'\n')            
    f.close()       
    return num_movies


if __name__ == '__main__':
    total_movs = get_items('English','USA','movs_eng_us.txt')
    print total_movs
    
