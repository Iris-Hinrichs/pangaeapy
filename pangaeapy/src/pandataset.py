# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 13:31:30 2018

@author: Robert Huber
@author: Markus Stocker
@author: Egor Gordeev
@author: Aarthi Balamurugan
"""
import time

import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import re
import io
import os

import pickle
from pangaeapy.src.exporter.pan_netcdf_exporter import PanNetCDFExporter
from pangaeapy.src.exporter.pan_frictionless_exporter import PanFrictionlessExporter

class PanProject:
    """PANGAEA Project Class
    This class creates objects which contain the project context information for each dataset
    
    Parameters
    ----------
    acronym : str
        The project acronym
    title : str
        The full title of the project
    URL : str
        The project website
    awardURI : str
        The unique identifier of the award e.g. a CORDIS URI
    
    
    Attributes
    ----------
    acronym : str
        The project acronym
    title : str
        The full title of the project
    URL : str
        The project website
    awardURI : str
        The unique identifier of the award e.g. a CORDIS URI
    
    """
    def __init__(self,label, name,URL=None, awardURI=None):
        self.label=label
        self.name=name
        self.URL=URL
        self.awardURI=awardURI
		
class PanLicence:
	"""PANGAEA Licence Class
	This class contains the licence information for each dataset
    """
	
	def __init__(self,label, name, URI=None):
		self.label=label
		self.name=name
		self.URI=URI
		
class PanAuthor:
    """PANGAEA Author Class.
    A simple helper class to declare 'author' objects which are associated as part of the metadata of a given PANGAEA dataset object
    
    Parameters
    ----------
    lastname : str
        The author's first name
    firstname : str
        The authors's last name
    ORCID : str
        The unique ORCID identifier assigned by orcid.org
    
    Attributes
    ----------
    lastname : str
        The author's first name
    firstname : str
        The authors's last name
    fullname : str
        Combination of lastname, firstname. This attribute is created by the constructor
    ORCID : str
        The unique ORCID identifier assigned by orcid.org
    """
    def __init__(self,lastname, firstname=None, orcid=None):
        self.lastname=lastname
        self.firstname=firstname
        self.fullname=self.lastname
        self.ORCID=orcid
        if firstname!=None and  firstname!='':
            self.fullname+=', '+self.firstname

class PanEvent:
    """ PANGAEA Event Class.
    An Event can be regarded as a named entity which is defined by the usage of a distinct method or device at a distinct location during a given time interval for scientific purposes.
    More infos on PANGAEA's Evenmts can be found here: https://wiki.pangaea.de/wiki/Event
    
    Parameters
    ----------
    label : str
        A label which is used to name the event
    latitude : float
        The latitude of the event location
    longitude : float
        The longitude of the event location
    elevation : float
        The elevation (relative to sea level) of the event location
    datetime : str
        The date and time of the event in ´%Y/%m/%dT%H:%M:%S´ format
    device : str
        The device which was used during the event
        
    Attributes
    ----------
    label : str
        A label which is used to name the event
    latitude : float
        The start latitude of the event location
    longitude : float
        The start longitude of the event location
    latitude2 : float
        The end latitude of the event location
    longitude2 : float
        The end longitude of the event location
    elevation : float
        The elevation (relative to sea level) of the event location
    datetime : str
        The start date and time of the event in ´%Y/%m/%dT%H:%M:%S´ format
    datetime2 : str
        The end date and time of the event in ´%Y/%m/%dT%H:%M:%S´ format
    device : str
        The device which was used during the event
    basis : str
        The basis or platform which was used during the event e.g. a ship
    location : str
        The location of the event
    campaign : PanCampaign
        The campaign during which the event was performed
    """
    def __init__(self, label, latitude=None, longitude=None, latitude2=None, longitude2=None, elevation=None, datetime=None, datetime2=None, device=None, basis=None, location=None, campaign=None):
        self.label=label
        if latitude !=None:
            self.latitude=float(latitude)
        else:
            self.latitude=None
        if longitude !=None:
            self.longitude=float(longitude)
        else:
            self.longitude=None
        if latitude2 !=None:
            self.latitude2=float(latitude2)
        else:
            self.latitude2=None
        if longitude2 !=None:
            self.longitude2=float(longitude2)
        else:
            self.longitude2=None
        if elevation !=None:
            self.elevation=float(elevation)
        else:
            self.elevation=None
        self.device=device
        self.basis=basis
        # -- NEED TO CARE ABOUT datetime2!!!
        self.datetime=datetime
        self.datetime2=datetime2
        self.location=location
        self.campaign=campaign
		
class PanCampaign:
    """PANGAEA Campaign class
	The campaign during which the event took place, e.g. a ship cruise or observatory deployment
	
	name : str
        The name of the campaign
    URI : str
        The campaign URI
    start : str
        The start date of the campaign
    end : str
        The end date of the campaign
    startlocation : str
        The start location of the campaign
    endlocation : str
        The end location of the campaign
    BSHID : str
        The BSH ID for the campaign
    expeditionprogram: str
        URL of the campaign report
	"""
    def __init__(self,name=None, URI=None, start=None, end=None, startlocation=None, endlocation=None, BSHID=None, expeditionprogram=None):
        
        self.name=name
        self.URI=URI
        self.start=start
        self.end=end
        self.startlocation=startlocation
        self.endlocation=endlocation
        self.BSHID=BSHID
        self.expeditionprogram=expeditionprogram
	
class PanParam:
    """ PANGAEA Parameter
    Shoud be used to create PANGAEA parameter objects. Parameter is used here to represent 'measured variables'
    
    Parameters
    ----------
    id : int
        the identifier for the parameter
    name : str
        A long name or title used for the parameter
    shortName : str
        A short name or label to identify the parameter
    param_type : str
        indicates the data type of the parameter (string, numeric, datetime etc..)
    source : str
        defines the category or source for a parameter (e.g. geocode, data, event)... very PANGAEA specific ;)
    unit : str
        the unit of measurement used with this parameter (e.g. m/s, kg etc..)
    terms : dict
        a dictionary containing al related terms for this parameter structure:{term:id}
    comment : str
        an optional comment explaining some details of the parameter

    
    Attributes
    ----------
    id : int
        the identifier for the parameter
    name : str
        A long name or title used for the parameter
    shortName : str
        A short name or label to identify the parameter
    synonym : dict
        A dictionary of synonyms for the parameter whcih e.g. is used by other archives or communities.
        The dict key indicates the namespace (possible values currently are CF and OS)
    type : str
        indicates the data type of the parameter (string, numeric, datetime etc..)
    source : str
        defines the category or source for a parameter (e.g. geocode, data, event)... very PANGAEA specific ;)
    unit : str
        the unit of measurement used with this parameter (e.g. m/s, kg etc..)
    format: str
        the number format string given by PANGAEA e.g ##.000 which defines the displayed precision of the number
    terms : dict
        a dictionary containing al related terms for this parameter {term:id}
    comment : str
        an optional comment explaining some details of the parameter
        
    
    
    """
    def __init__(self, id, name, shortName, param_type, source, unit=None, unit_id = None, format=None, terms =[], comment=None):
        self.id=id
        self.name=name
        self.shortName=shortName
        # Synonym namespace dict predefined keys are CF: CF variables (), OS:OceanSites, SD:SeaDataNet abbreviations (TEMP, PSAL etc..)
        ns=('CF','OS','SD')
        self.synonym=dict.fromkeys(ns)
        self.type=param_type
        self.source=source
        self.unit=unit
        self.unit_id = unit_id
        self.format=format
        self.terms =terms
        self.comment = comment

    def addSynonym(self,ns, name, uri=None, id=None, unit=None, unit_id = None):
        """
        Creates a new synonym for a parameter which is valid within the given name space. Synonyms are stored in the synonym attribute which is a dictionary
        
        Parameters
        ----------
        name : str
            the name of the synonym
        id : str
            the internal ID of the term used at its auhority ontology
        uri : str
            the URI (ideally actionable) leading to its auhority ontology entry/web page
        ns : str
            the namespace indicator for the sysnonym
        unit : str
            in case another unit expression is used for the synonym parameter within its namespace
        unit_id : str
            the id, UI or URN for the unit
        """
        self.synonym[ns]={'name':name,'id':id, 'uri':uri, 'unit':unit,'unit_id':unit_id}
    
class PanDataSet:
    """ PANGAEA DataSet
    The PANGAEA PanDataSet class enables the creation of objects which hold the necessary information, including data as well as metadata, to analyse a given PANGAEA dataset.
    
    Parameters
    ----------
    id : str
        The identifier of a PANGAEA dataset. An integer number or a DOI is accepted here
    deleteFlag : str
        in case quality flags are avialable, this parameter defines a flag for which data should not be included in the data dataFrame.
        Possible values are listed here: https://wiki.pangaea.de/wiki/Quality_flag
    addQC : boolean
        adds a QC column for each parameter which contains QC flags
    enable_cache : boolean
        If set to True, PanDataSet objects are cached as pickle files on the local home directory within a directory called 'pangaeapy_cache' in order to avoid unnecessary downloads.
    include_data : boolean
        determines if data table is downloaded and added to the self.data dataframe. If you are interested in metadata only set this to False
        
    Attributes
    ----------
    id : str
        The identifier of a PANGAEA dataset. An integer number or a DOI is accepted here
    uri : str
        The PANGAEA DOI (alternative label)
    doi : str
        The PANGAEA DOI
    title : str
        The title of the dataset
    abstract: str
        the abstract or summary of the dataset
    year : int
        The publication year of the dataset
    authors : list of PanAuthor
        a list containing the PanAuthot objects (author info) of the dataset
    citation : str
        the full citation of the dataset including e.g. author, year, title etc..
    params : list of PanParam
        a list of all PanParam objects (the parameters) used in this dataset
    parameters : list of PanParam
        synonym for self.params
    events : list of PanEvent
        a list of all PanEvent objects (the events) used in this dataset
    projects : list of PanProject
        a list containing the PanProjects objects referenced by this dataset
    mintimeextent : str
        a string containing the min time of data set extent
    maxtimeextent : str
        a string containing the max time of data set extent
    data : pandas.DataFrame
        a pandas dataframe holding all the data
    loginstatus : str
        a label which indicates if the data set is protected or not default value: 'unrestricted'            
    isParent : boolean
        indicates if this dataset is a parent data set within a collection of child data sets
    children : list
        a list of DOIs of all child data sets in case the data set is a parent data set
	moratorium : str
		a label which provides the date until the dataset is under moratorium
	datastatus : str
		a label which provides the detail about the status of the dataset whether it is published or in review
	registrystatus : str
		a string which indicates the registration status of a dataset
	licence : PanLicence
	    a licence object, usually creative commons
    """
    def __init__(self, id=None,paramlist=None, deleteFlag='', addQC=False, QCsuffix = None, enable_cache=False, include_data=True):
        self.module_dir = os.path.dirname(os.path.dirname(__file__))
        ### The constructor allows the initialisation of a PANGAEA dataset object either by using an integer dataset id or a DOI
        self.setID(id)
        self.ns= {'md':'http://www.pangaea.de/MetaData'}        
        # Mapping should be moved to e.g netCDF class/module??
        #moddir = os.path.dirname(os.path.abspath(__file__))
        #self.CFmapping=pd.read_csv(moddir+'\\PANGAEA_CF_mapping.txt',delimiter='\t',index_col='ID')
        self.cache=enable_cache
        self.uri = self.doi = '' #the doi
        self.isParent=False
        self.params=dict()
        self.parameters = self.params
        self.defaultparams=['Latitude','Longitude','Event','Elevation','Date/Time']
        self.paramlist=paramlist
        self.paramlist_index=[]
        self.events=[]
        self.projects=[]
        self.licence=None
        #allowed geocodes for netcdf generation which are used as xarray dimensions not needed in the moment
        self._geocodes={1599:'Date_Time',1600:'Latitude',1601:'Longitude',1619:'Depth water'}
        self.data =pd.DataFrame()
        self.title=None
        self.abstract = None
        self.moratorium=None
        self.datastatus=None
        self.registrystatus=None
        self.citation=None
        self.year=None
        self.date=None
        self.mintimeextent=None
        self.maxtimeextent=None
        self.topotype = None
        self.authors=[]
        self.error=None
        self.loginstatus='unrestricted'
        self.allowNetCDF=True        
        self.eventInMatrix=False
        self.deleteFlag=deleteFlag
        self.children=[]
        self.include_data=include_data
        self.qc_column_suffix='_QC'
        if QCsuffix:
            self.qc_column_suffix = QCsuffix
        #no symbol = valid(default)
        #? = questionable(?0.345)
        #/ = not valid( / 23.56)
        #* = unknown(*0.999)
        # = individual definition (#999)

        self.quality_flags={'ok':'valid','?':'questionable','/':'not_valid','*':'unknown'}
        self.quality_flag_replace={'ok':0,'?':1,'/':2,'*':3}
        if self.id != None:
            gotData=False
            if self.cache==True:
                print('Caching activated..trying to load data and metadata from cache')
                gotData=self.from_pickle()
            if not gotData:        
                #print('trying to load data and metadata from PANGAEA')
                self.setMetadata()
                self.defaultparams=[s for s in self.defaultparams if s in self.params.keys()]            
                if self.loginstatus=='unrestricted' and self.isParent!=True:
                    self.setData(addQC=addQC)
                    if self.paramlist!=None:
                        if  len(self.paramlist)!=len(self.paramlist_index):
                            print('PROBLEM: '+self.error)
                    if self.cache==True:
                       self.to_pickle() 
                else:
                    print('PROBLEM: '+self.error)
                
                
    def from_pickle(self, cachedir=''):
        """
        Reads a PanDataSet object from a pickle file
        
        Parameters
        ----------
        cachedir : str
            the name of the directory
        """
        home = os.path.expanduser("~")
        ret=False
        if cachedir=='':
            cachedir=home+'/'+'pangaeapy_cache'

        if os.path.exists(cachedir+'/'+str(self.id)+'_data.pik'):
            try:
                f = open(cachedir+'/'+str(self.id)+'_data.pik', 'rb')
                tmp_dict = pickle.load(f)
                f.close()         
                self.__dict__.update(tmp_dict)
                ret=True
            except:
                ret=False
            
            
        else:
            ret=False
        return ret
                
    def to_pickle(self,cachedir=''):
        """
        Writes a PanDataSet object to a pickle file
        
        Parameters
        ----------
        cachedir : str
            the name of the directory
        """
        home = os.path.expanduser("~")
        if cachedir=='':
            cachedir=home+'/'+'pangaeapy_cache'
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        f = open(cachedir+'/'+str(self.id)+'_data.pik', 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()
        
    
    def setID (self, id):
        """
        Initialize the ID of a data set in case it was not defined in the constructur
        Parameters
        ----------
        id : str
            The identifier of a PANGAEA dataset. An integer number or a DOI is accepted here
        """
        if type(id) == int:
            self.id = id
        else:
            idmatch = re.search(r'10\.1594\/PANGAEA\.([0-9]+)$', id)
            if idmatch is not None:
                self.id = idmatch[1]
            else:
                print('Invalid Identifier')

    
            
    def _getID(self,panparidstr):
        panparidstr=panparidstr[panparidstr.rfind('.')+1:]
        panparId=re.match(r"([a-z]+)([0-9]+)",panparidstr)
        if panparId:
            return panparId.group(2)
        else:
            return False
        
    
    def _setEvents(self, panXMLEvents):
        """
        Initializes the list of Events from a metadata XML file for a given pangaea dataset. 
        """
        for event in panXMLEvents:

            eventElevation=eventDateTime=eventDateTime2 = None
            eventDevice=eventLabel=eventBasis = None
            campaign_name= campaign_URI=campaign_start=campaign_end = None
            eventLongitude=eventLatitude=eventLatitude2=eventLongitude2=eventLocation = None
            startlocation =endlocation=BSHID=expeditionprogram = None

            if event.find('md:elevation',self.ns)!=None:                
                eventElevation=event.find('md:elevation',self.ns).text
            if event.find('md:dateTime',self.ns)!=None:
                eventDateTime= event.find('md:dateTime',self.ns).text
            if event.find('md:dateTime2',self.ns)!=None:
                eventDateTime2= event.find('md:dateTime2',self.ns).text
            if event.find('md:longitude',self.ns)!=None:
                eventLongitude= event.find('md:longitude',self.ns).text
            if event.find('md:latitude',self.ns)!=None:
                eventLatitude= event.find('md:latitude',self.ns).text
            if event.find('md:longitude2',self.ns)!=None:
                eventLongitude2= event.find('md:longitude2',self.ns).text
            if event.find('md:latitude2',self.ns)!=None:
                eventLatitude2= event.find('md:latitude2',self.ns).text
            if event.find('md:label',self.ns)!=None:
                eventLabel= event.find('md:label',self.ns).text
            if event.find('md:location/md:name',self.ns)!=None:
                eventLocation= event.find('md:location/md:name',self.ns).text
            if event.find('md:basis/md:name',self.ns)!=None:
                eventBasis= event.find('md:basis/md:name',self.ns).text
            if event.find('md:method/md:name',self.ns)!=None:
                eventDevice= event.find('md:method/md:name',self.ns).text
            if event.find("md:campaign", self.ns)!=None:
                campaign=event.find("md:campaign", self.ns)
                if campaign.find('md:name',self.ns)!=None:
                    campaign_name= campaign.find('md:name',self.ns).text
                if campaign.find('md:URI',self.ns)!=None:
                    campaign_URI= campaign.find('md:URI',self.ns).text
                if campaign.find('md:start',self.ns)!=None:
                    campaign_start= campaign.find('md:start',self.ns).text
                if campaign.find('md:end',self.ns)!=None:
                    campaign_end= campaign.find('md:end',self.ns).text
                if campaign.find('md:attribute[@name="Start location"]',self.ns)!=None:
                    startlocation= campaign.find('md:attribute[@name="Start location"]',self.ns).text
                if campaign.find('md:attribute[@name="End location"]',self.ns)!=None:
                    endlocation= campaign.find('md:attribute[@name="End location"]',self.ns).text
                if campaign.find('md:attribute[@name="BSH ID"]',self.ns)!=None:
                    BSHID= campaign.find('md:attribute[@name="BSH ID"]',self.ns).text
                if campaign.find('md:attribute[@name="Expedition Program"]',self.ns)!=None:
                    expeditionprogram= campaign.find('md:attribute[@name="Expedition Program"]',self.ns).text
                else:
                    expeditionprogram=None
                eventCampaign=PanCampaign(campaign_name,campaign_URI,campaign_start,campaign_end,startlocation,endlocation,BSHID,expeditionprogram)
            else:
                eventCampaign=None

            self.events.append(PanEvent(eventLabel, 
                                        eventLatitude, 
                                        eventLongitude,
                                        eventLatitude2,
                                        eventLongitude2,
                                        eventElevation,
                                        eventDateTime,
                                        eventDateTime2,
                                        eventDevice,
                                        eventBasis,									
                                        eventLocation,
                                        eventCampaign
                                        ))

    def _setParameters(self, panXMLMatrixColumn):
        """
        Initializes the list of parameter objects from the metadata XML info
        """
        coln=dict()
        if panXMLMatrixColumn!=None:
            panGeoCode=[]
            for matrix in panXMLMatrixColumn:  
                panparCFName=None
                paramstr=matrix.find("md:parameter", self.ns)
                panparID=int(self._getID(str(paramstr.get('id'))))  

                panparShortName='';
                if(paramstr.find('md:shortName',self.ns) != None):
                    panparShortName=paramstr.find('md:shortName',self.ns).text
                    panparIndex = panparShortName
                    #Rename duplicate column headers
                    if panparShortName in coln:
                        coln[panparShortName]+=1
                        panparIndex=panparShortName+'_'+str(coln[panparShortName])
                    else:
                        coln[panparShortName]=1
                panparType=matrix.get('type')
                panparUnit=None
                if(paramstr.find('md:unit',self.ns)!=None):
                    panparUnit=paramstr.find('md:unit',self.ns).text
                panparComment=None
                if(matrix.find('md:comment',self.ns)!=None):
                    panparComment=matrix.find('md:comment',self.ns).text
                panparFormat=matrix.get('format')
                if panparShortName=='Event':
                    self.eventInMatrix=True
                #if panparID in self.CFmapping.index:
                #    panparCFName=self.CFmapping.at[panparID,'STDNAME']
                #Add information about terms/ontologies used:
                termlist=[]
                for terminfo in paramstr.findall('md:term', self.ns):
                    termid = None
                    termname = None
                    if terminfo.find("md:name", self.ns) != None:
                        termname = terminfo.find("md:name", self.ns).text
                        termid = int(self._getID(str(terminfo.get('id'))))
                        terminologyid = int(terminfo.get('terminologyId'))
                        termlist.append({'id':termid,'name': str(termname),'ontology':terminologyid})

                self.params[panparIndex]=PanParam(id=panparID,name=paramstr.find('md:name',self.ns).text,shortName=panparShortName,param_type=panparType,source=matrix.get('source'),unit=panparUnit,format=panparFormat,terms=termlist, comment=panparComment)
                self.parameters = self.params
                if panparType=='geocode':
                    if panparShortName in panGeoCode:
                        self.allowNetCDF = False
                        self.error = 'Data set contains duplicate Geocodes'
                        print(self.error)
                    else:
                        panGeoCode.append(panparShortName)

        
    def getEventsAsFrame(self):
        """
        For more convenient handling of event info, this method returns a dataframe containing all events with their attributes as columns
        Please note that this version just takes campaign names, not other campaign attributes
        """
        df=pd.DataFrame()
        try:
            df = pd.DataFrame([ev.__dict__ for ev in self.events ])
            df['campaign'] = df['campaign'].apply(lambda x: x.name)
        except:
            pass
        return df
        
    def setData(self, addEventColumns=True, addQC=False):
        """
        This method populates the data DataFrame with data from a PANGAEA dataset.
        In addition to the data given in the tabular ASCII file delivered by PANGAEA.
        
        
        Parameters:
        -----------
        addEventColumns : boolean
            In case Latitude, Longititude, Elevation, Date/Time and Event are not given in the ASCII matrix, which sometimes is possible in single Event datasets, 
            the setData could add these columns to the dataframe using the information given in the metadata for Event. Default is 'True'
        addQC : boolean
            If this is set to True, pangaeapy adds a QC column in which the quality flags are separated. Each new column is named after the orgininal column plus a "_qc" suffix.

        """

        # converting list of parameters` short names (from user input) to the list of parameters` indexes
        # the list of parameters` indexes is an argument for pd.read_csv
        if self.paramlist!=None:
            self.paramlist+=self.defaultparams
            for parameter in self.paramlist:
                iter=0
                for shortName in self.params.keys():
                    if parameter==shortName:
                        self.paramlist_index.append(iter)
                    iter+=1
            if len(self.paramlist)!=len(self.paramlist_index):
                self.error="Error entering parameters`short names!"
        else:
            self.paramlist_index=None
        if self.include_data==True:
            dataURL="https://doi.pangaea.de/10.1594/PANGAEA."+str(self.id)+"?format=textfile"
            panDataTxt= requests.get(dataURL).text       
            panData = re.sub(r"/\*(.*)\*/", "", panDataTxt, 1, re.DOTALL).strip() 
            #Read in PANGAEA Data    
            self.data = pd.read_csv(io.StringIO(panData), index_col=False ,error_bad_lines=False,sep=u'\t',usecols=self.paramlist_index,names=list(self.params.keys()),skiprows=[0])
            # add geocode/dimension columns from Event

            #if addEventColumns==True and self.topotype!="not specified":
            if addEventColumns==True:
                if len(self.events)==1:
                    if 'Event' not in self.data.columns:
                        self.data['Event']=self.events[0].label
                        self.params['Event']=PanParam(0,'Event','Event','string','data',None)
                if len(self.events)>=1:              
                    addEvLat=addEvLon=addEvEle=addEvDat=False
                    if 'Event' in self.data.columns:
                        if 'Latitude' not in self.data.columns:
                            addEvLat=True
                            self.data['Latitude']=np.nan
                            self.params['Latitude']=PanParam(1600,'Latitude','Latitude','numeric','geocode','deg')
                        if 'Longitude' not in self.data.columns: 
                            addEvLon=True
                            self.data['Longitude']=np.nan
                            self.params['Longitude']=PanParam(1601,'Longitude','Longitude','numeric','geocode','deg')
                        if 'Elevation' not in self.data.columns:  
                            addEvEle=True
                            self.data['Elevation']=np.nan
                            self.params['Elevation']=PanParam(8128,'Elevation','Elevation','numeric','geocode','m')
                        if 'Date/Time' not in self.data.columns:
                            self.data['Date/Time']=np.nan
                            self.params['Date/Time']=PanParam(1599,'Date/Time','Date/Time','numeric','geocode','')
                            
                        for iev,pevent in enumerate(self.events): 
                            if pevent.latitude is not None and addEvLat==True:
                                self.data.loc[(self.data['Event']== pevent.label) & (self.data['Latitude'].isnull()),['Latitude']]=self.events[iev].latitude
                            if pevent.longitude is not None and addEvLon:
                                self.data.loc[(self.data['Event']== pevent.label) & (self.data['Longitude'].isnull()),['Longitude']]=self.events[iev].longitude
                            if pevent.elevation is not None and addEvEle:
                                self.data.loc[(self.data['Event']== pevent.label) & (self.data['Elevation'].isnull()),['Elevation']]=self.events[iev].elevation
                            if pevent.datetime is not None and addEvDat:
                                self.data.loc[(self.data['Event']== pevent.label) & (self.data['Date/Time'].isnull()),['Date/Time']]=self.events[iev].datetime
    
            # -- delete values with given QC flags
            if self.deleteFlag!='':
                if self.deleteFlag=='?' or self.deleteFlag=='*':
                    self.deleteFlag="\\"+self.deleteFlag
                self.data.replace(regex=r'^'+self.deleteFlag+'{1}.*',value='',inplace=True)      
            # --- Replace Quality Flags for numeric columns   
            if addQC==False:
                self.data.replace(regex=r'^[\?/\*#\<\>]',value='',inplace=True)
            # --- Delete empty columns
            self.data=self.data.dropna(axis=1, how='all')
            #print(self.params.keys())
            for paramcolumn in list(self.params.keys()):
                if paramcolumn not in self.data.columns:
                    del self.params[paramcolumn]
            # --- add QC columns
                elif addQC==True:
                    print(paramcolumn,self.params[paramcolumn].type)
                    #if self.params[paramcolumn].type=='numeric' and (self.params[paramcolumn].source =='data' or paramcolumn=='Depth water'):
                    if self.params[paramcolumn].type in['numeric','datetime']:
                        self.data[[paramcolumn + self.qc_column_suffix,paramcolumn]]=self.data[paramcolumn].astype(str).str.extract(r'(^[\*/\?])?(.+)')
                        self.data[paramcolumn + self.qc_column_suffix].fillna(value='ok', inplace=True)
                        self.data[paramcolumn + self.qc_column_suffix].replace(to_replace=self.quality_flag_replace, inplace=True)
                        if self.params[paramcolumn].source =='data':
                            ptype = 'qc'
                        else:
                            #geocodeqc
                            ptype ='gqc'
                        self.params[paramcolumn + self.qc_column_suffix] = PanParam(self.params[paramcolumn].id+1000000000,self.params[paramcolumn].name + self.qc_column_suffix,self.params[paramcolumn].shortName + self.qc_column_suffix, source='pangaeapy',param_type=ptype)

            # --- Adjust Column Data Types
            self.data = self.data.apply(pd.to_numeric, errors='ignore')
            if 'Date/Time' in self.data.columns:
                self.data['Date/Time'] = pd.to_datetime(self.data['Date/Time'], format='%Y/%m/%dT%H:%M:%S')
        
    def _setCitation(self):
        citationURL="https://doi.pangaea.de/10.1594/PANGAEA."+str(self.id)+"?format=citation_text&charset=UTF-8"
        r=requests.get(citationURL)
        if r.status_code!=404:
            self.citation=r.text
        
    def setMetadata(self):
        """
        The method initializes the metadata of the PanDataSet object using the information of a PANGAEA metadata XML file.
        
        """
        self._setCitation()
        metaDataURL="https://doi.pangaea.de/10.1594/PANGAEA."+str(self.id)+"?format=metainfo_xml"
        #metaDataURL="https://ws.pangaea.de/es/pangaea/panmd/"+str(self.id)
        r=requests.get(metaDataURL)
        if r.status_code==429:
            print('Received too many requests error (429)...')
            sleeptime = 1
            if r.headers.get('retry-after'):
                sleeptime = r.headers.get('retry-after')
            print('Sleeping for :'+str(sleeptime)+'sec before retrying the request')
            if int(sleeptime) < 1:
                sleeptime=1
            time.sleep(int(sleeptime))
            r = requests.get(metaDataURL)
            print('After repeating request, got status code: '+str(r.status_code))

        if r.status_code!=404:
            try:
                r.raise_for_status()
                xmlText=r.text
                xml = ET.fromstring(xmlText)
                self.loginstatus=xml.find('./md:technicalInfo/md:entry[@key="loginOption"]',self.ns).get('value')
                if self.loginstatus!='unrestricted':
                    self.error='Data set is protected'                
                hierarchyLevel=xml.find('./md:technicalInfo/md:entry[@key="hierarchyLevel"]',self.ns)
                if hierarchyLevel!=None:
                    if hierarchyLevel.get('value')=='parent':
                        self.error='Data set is of type parent, please select one of its child datasets'
                        self.isParent=True
                        self._setChildren()
                self.title=xml.find("./md:citation/md:title", self.ns).text
                if xml.find("./md:abstract", self.ns)!=None:
                    self.abstract = xml.find("./md:abstract", self.ns).text
                self.datastatus=xml.find('./md:technicalInfo/md:entry[@key="status"]',self.ns).get('value')
                self.registrystatus=xml.find('./md:technicalInfo/md:entry[@key="DOIRegistryStatus"]',self.ns).get('value')
                if xml.find('./md:technicalInfo/md:entry[@key="moratoriumUntil"]',self.ns) != None:
                    self.moratorium=xml.find('./md:technicalInfo/md:entry[@key="moratoriumUntil"]',self.ns).get('value')
                self.year=xml.find("./md:citation/md:year", self.ns).text
                self.date=xml.find("./md:citation/md:dateTime", self.ns).text
                self.doi=self.uri=xml.find("./md:citation/md:URI", self.ns).text
                #extent
                if xml.find("./md:extent/md:temporal/md:minDateTime", self.ns)!=None:
                    self.mintimeextent=xml.find("./md:extent/md:temporal/md:minDateTime", self.ns).text
                if xml.find("./md:extent/md:temporal/md:maxDateTime", self.ns)!=None:
                    self.maxtimeextent=xml.find("./md:extent/md:temporal/md:maxDateTime", self.ns).text
                
                topotypeEl=xml.find("./md:extent/md:topoType", self.ns)
                if topotypeEl!=None:
                    self.topotype=topotypeEl.text
                else:
                    self.topotype=None
                for author in xml.findall("./md:citation/md:author", self.ns):
                    lastname=None
                    firstname=None
                    orcid=None
                    if author.find("md:lastName", self.ns)!=None:
                        lastname=author.find("md:lastName", self.ns).text
                    if author.find("md:firstName", self.ns)!=None:
                        firstname=author.find("md:firstName", self.ns).text
                    if author.find("md:orcid", self.ns)!=None:
                        orcid=author.find("md:orcid", self.ns).text
                    self.authors.append(PanAuthor(lastname, firstname,orcid))
                for project in xml.findall("./md:project", self.ns):
                    label=None
                    name=None
                    URI=None
                    awardURI=None
                    if project.find("md:label", self.ns)!=None:
                        label=project.find("md:label", self.ns).text
                    if project.find("md:name", self.ns)!=None:
                        name=project.find("md:name", self.ns).text
                    if project.find("md:URI", self.ns)!=None:
                        URI=project.find("md:URI", self.ns).text
                    if project.find("md:award/md:URI", self.ns)!=None:
                        awardURI=project.find("md:award/md:URI", self.ns).text
                    self.projects.append(PanProject(label, name, URI, awardURI))
                if xml.find("./md:license",self.ns) != None:
                    license = xml.find("./md:license",self.ns)
                    label=None
                    name=None
                    URI=None
                    if license.find("md:label", self.ns)!=None:
                        label=license.find("md:label", self.ns).text
                    if license.find("md:name", self.ns)!=None:
                        name=license.find("md:name", self.ns).text
                    if license.find("md:URI", self.ns)!=None:
                        URI=license.find("md:URI", self.ns).text
                    self.licence = PanLicence(label, name, URI)

                panXMLMatrixColumn=xml.findall("./md:matrixColumn", self.ns)
                self._setParameters(panXMLMatrixColumn)
                panXMLEvents=xml.findall("./md:event", self.ns)
                self._setEvents(panXMLEvents)
            except requests.exceptions.HTTPError as e:
                print(e)
        else:
            self.error='Data set does not exist'
            print(self.error)

    def _setChildren(self):
        childqueryURL="https://www.pangaea.de/advanced/search.php?q=incollection:"+str(self.id)+"&count=1000"
        r = requests.get(childqueryURL)
        if r.status_code != 404:
            s = r.json()
            for p in s['results']: 
                self.children.append(p['URI'])
                #print(p['URI'])
            
    def getGeometry(self):
        """
        Sometimes the topotype attribute has not been set correctly during the curation process. 
        This method returns the real geometry (topographic type) of the dataset based on the x,y,z and t information of the data frame content.
        Still a bit experimental..
        """
        geotype=0
        zgroup=['Latitude','Longitude']
        tgroup=['Latitude','Longitude']
        locgrp=['Latitude','Longitude']
        p=pz=pt=len(self.data.groupby(locgrp))
        t=z=None
        
        if 'Date_Time' in self.data.columns:
            t='Date_Time'
        if 'Depth_water' in self.data.columns:
            z='Depth_water'
        elif 'Depth' in self.data.columns:
            z='Depth'
        elif 'Depth_ice_snow' in self.data.columns:
            z='Depth_ice_snow'
        elif 'Depth_soil' in self.data.columns:
            z='Depth_soil'

        if t!=None:
            tgroup.append(t)
            pt=len(self.data.groupby(tgroup))
        if z!=None:
            zgroup.append(z)
            pz=len(self.data.groupby(zgroup))
        if p==1:
            if pt==1 and pz==1:
                geotype='point'
            elif pt>=1:
                if pz==1 or len(self.events)==1:
                    geotype='timeSeries'
                else: 
                    geotype='timeSeriesStack'
            else:
                geotype='profile'
        else:
            if p==pz:
                geotype='trajectory'
            elif pt>pz:
                geotype='timeSeriesProfile'
            else:
                geotype='trajectoryProfile'
        return geotype


    """
            The method returns translates the parameter object list into a dictionary 
    """
    def getParamDict(self):
        paramdict={'shortName':[],'name':[],'unit':[],'type':[],'format':[]}
        for param_key, param_value in self.params.items():
            paramdict['shortName'].append(param_key)
            paramdict['name'].append(param_value.name)
            paramdict['unit'].append(param_value.unit)
            paramdict['type'].append(param_value.type)
            paramdict['format'].append(param_value.format)
        return paramdict

    """
            The method returns a set of basic information about the PANGAEA dataset
    """
    def info(self):
        print('Citation:')
        print(self.citation)
        print()
        print('Toptype:')
        print(self.topotype)
        print()
        print('Parameters:')
        paramdf=pd.DataFrame(self.getParamDict())
        print(paramdf)
        print()
        print('Data: (first 5 rows)')
        print(self.data.head(5))

    def rename_column(self,old_name, new_name):
        self.params[new_name] = self.params.pop(old_name)
        self.params[new_name].name = new_name
        self.params[new_name].shortName = new_name
        self.data.rename(columns={old_name:new_name}, inplace = True)


    def to_netcdf(self, filelocation=None, type='sdn'):
        """
        This method creates a NetCDF file using PANGAEA data. It offers two different flavors: SeaDataNet NetCDF and an
        experimental internal format using NetCDF 4 groups.
        Currently the method only supports simple types such as timeseries and profiles.
        The method created files are named as follows: [PANGAEA ID]_[type].cf

        Parameters:
        -----------
        filelocation : str
            Indicates the location (directory) where the NetCDF file will be saved
        type : str
            This parameter sets the NetCDF profile type. Allowed values are 'sdn' (SeaDataNet) and 'pan' (PANGAEA style)
        """

        netcdfexporter = PanNetCDFExporter(self, filelocation,)
        netcdfexporter.create(style=type)

    def to_frictionless(self, filelocation=None, compress = False):
        """
        This method creates a frictionless data package (https://specs.frictionlessdata.io/data-package) file using PANGAEA metadata and data.
        A package will be saved as directory
        The method created directories are named as follows: [PANGAEA ID]_frictionless

        Parameters:
        -----------
        filelocation : str
            Indicates the location (directory) where the NetCDF file will be saved
        compress : Boolean
            If the directory shall be zip compressed or not
        """

        frictionless_exporter = PanFrictionlessExporter(self, filelocation)
        ret= frictionless_exporter.create()
        return ret