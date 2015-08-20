import urllib.request
import zipfile
import os
import re
import json
import sys
from optparse import OptionParser 
import time 
             
SPE_DOWNLOAD_URL = "https://github.com/IBMPredictiveAnalytics/repos_name/raw/master/STATS_OPEN_PROJECT.spe"
IMG_DOWNLOAD_URL = "https://raw.githubusercontent.com/IBMPredictiveAnalytics/repos_name/master/default.png"
FILE_NAME= "MANIFEST.MF"
INDEX_FILE = 'index.json'
INDENT = '    '
START_WORDS = "{\n\"productname_extension_index\":[\n"

class MetaObj:    
    KEY = 0
    VAL = 1
    '''
    initialize a MeatObj to save manifest content 
    '''
    def __init__(self,meta_file):  
        self.key_list = []
        meta_content = '' 
        try:
            meta_content, self.key_list = self.parseMetaContent(meta_file)
        except IOError as e:
            print("File open error: "+str(e))
            sys.exit(0)
        
        self.meta_list = []        
        for key in self.key_list:
            val = re.findall(key+"\s*:\s*(.+?)\n",meta_content,re.S)
            if len(val) == 0:
                continue
            self.meta_list.append(tuple([key,val[0]]))
        
    
    '''
    Input: manifest file path
    Output: A string eliminated space and \n in one item 
    '''
    def parseMetaContent(self,meta_file):
        meta_content = ''
        try:
            fp = open(meta_file, 'r')
            meta_content = fp.read()
        except IOError as err:
            raise err
        
        if meta_content != '':
            line_list = meta_content.split('\n')
            modified_str = ''
            temp = ''
            key_list = []
            for item in line_list:           
                if item[0:1] == ' ':
                    temp = temp+item[1:]            
                else:
                    if temp != '':
                        modified_str = modified_str+temp+'\n'
                    temp = ''
                    temp = item
                    
                    key = re.findall("(.+?)\s*:",item)
                    if len(key) != 0:
                        key_list.append(key[0])
        return modified_str, key_list
    
    def generateExtensionJSON(self):
        try:
            if len(self.meta_list) == 0:
                raise Exception("Error format of MANIFEST file")
        except Exception as e:
            raise e
        
        extension_json = INDENT+INDENT+"\"extension_detail_info\": {\n"    
        for item in  self.meta_list:
            extension_json += INDENT*3 + "\"" + item[MetaObj.KEY] + "\"" + ":" + "\"" + item[MetaObj.VAL]+ "\",\n" 
        
        extension_json = extension_json[0:-2]+'\n'
        extension_json += INDENT*2 + "}\n"  
        return extension_json        

def getWholeProductName(product_name):
    if(product_name == "stats"):
        return "SPSS Statistics"
    else:
        return "SPSS Modeler"

def downloadFile(spe_path,index_path, product_name):
    api_url = "https://api.github.com/orgs/ibmpredictiveanalytics/repos?per_page=1000"
    raw_spe_url = "https://github.com/IBMPredictiveAnalytics/repos_name/raw/master/repos_name.spe"
    raw_info_json_url = 'https://raw.githubusercontent.com/IBMPredictiveAnalytics/repos_name/master/info.json'

    #key_list for repository info.json
    key_list = ['type', 'provider', 'software', 'language', 'category', 'promotion']
    
    api_json_data = json.loads(urllib.request.urlopen(api_url).read().decode('utf-8'))
    
    index_for_web_json = re.sub('productname', product_name, START_WORDS)
    whole_product_name = getWholeProductName(product_name)
     
    index_for_web = open(os.path.join(index_path, INDEX_FILE),'w')
    
    cur_time = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    root_spe_dir = "spe"+cur_time
    
    os.chdir(spe_path)
    os.mkdir(root_spe_dir)
    root_spe_dir = os.path.abspath(root_spe_dir)
    os.chdir(root_spe_dir)
    
    i=0
    print("start to get repo data from github ...")
    for item in api_json_data:                
        repo_name = item['name']
        i+=1
        print("\n\nStart to read "+str(i)+"th repo ...")
        #ignore .io repository
        if('IBMPredictiveAnalytics.github.io' == repo_name):
            continue
        
        repo_desc = item['description']
        repo_push_time = item['pushed_at']
        repo_info_json_url = re.sub('repos_name', repo_name, raw_info_json_url)
        try:
            repo_info_json = json.loads(urllib.request.urlopen(repo_info_json_url).read().decode('utf-8'))
        except:
            print("This repo '"+repo_name+"' does not have info.json. Please check!"+"\nSwitch to next repo.\n\n\n")
            continue   
        
        if type(repo_info_json['software']) == list:
            repo_software = repo_info_json['software'][0]
        else:
            repo_software = repo_info_json['software']
        print(repo_software)
        if repo_software != whole_product_name:
            print("This is not a " + whole_product_name + " repo.\nSwitch to next repo.\n\n\n")
            continue
        
        repo_spe_url = re.sub('repos_name', repo_name, raw_spe_url)
        spe_name = repo_name+".spe"
        try:
            urllib.request.urlretrieve(repo_spe_url, spe_name)
            srcZip = zipfile.ZipFile(spe_name, "r",zipfile.ZIP_DEFLATED)
        except:
            print("This repo '"+repo_name+"' does not have spe package. Please check!"+"\nSwitch to next repo.\n\n\n")
            continue
        
        for file in srcZip.namelist():
            if not os.path.isdir(os.path.abspath(repo_name)):     
                os.mkdir(os.path.abspath(repo_name))
            if FILE_NAME in file:
                srcZip.extract(file, os.path.abspath(repo_name))
        srcZip.close()        
        
        json_item = INDENT+'{\n'
        json_item += INDENT*2 + "\"repository\":" +"\"" + repo_name +"\",\n" 
        json_item += INDENT*2 + "\"description\":" +"\"" + repo_desc +"\",\n"
        json_item += INDENT*2 + "\"pushed_at\":" +"\"" + repo_push_time +"\",\n" 
        
        for key in key_list:
            if type(repo_info_json[key]) == list:
                val = repo_info_json[key][0]
            else:
                val = repo_info_json[key]
            json_item += INDENT*2 + "\"" + key + "\":" + "\"" + val + "\",\n"
        
        json_item += INDENT*2 + "\"download_link\":" +"\"" + re.sub('repos_name', repo_name, SPE_DOWNLOAD_URL) +"\",\n"
        json_item += INDENT*2 + "\"image_link\":" +"\"" + re.sub('repos_name', repo_name, IMG_DOWNLOAD_URL) +"\",\n"
        
        print(os.path.abspath(repo_name))
        os.chdir(os.path.abspath(repo_name))
        meta_path = os.path.join(os.path.abspath('META-INF'), FILE_NAME)
        print(meta_path)
        metaObj = MetaObj(meta_path)
        extension_json = metaObj.generateExtensionJSON()
        
        json_item += extension_json
        json_item += INDENT + "},\n"  
        index_for_web_json += json_item
        os.chdir(root_spe_dir)
    print("The script completed successfully!")
    index_for_web_json = index_for_web_json[0:-2]
    index_for_web_json += '\n]\n}'
    index_for_web.write(index_for_web_json)  
    index_for_web.close()


if __name__ == '__main__':    
    usage = "usage: %prog [options] arg1 arg2 arg3"  
    parser = OptionParser(usage)  
    parser.add_option("-s", "--spedir", dest="spedir", action='store', help="Directory to save spe.")
    parser.add_option("-o", "--output", dest="outdir", action='store', help="Choose a dir to save index file.")
    parser.add_option("-p", "--product", dest="productName", action='store', help="Choose index for which product: 1. SPSS Modeler 2. SPSS Statistics.")
    (options, args) = parser.parse_args() 
    print(options.productName)

    if not os.path.isdir(options.spedir):
        parser.error("Please input a valid directory to save spe.")  
    if not os.path.isdir(options.outdir):
        parser.error("Please input a valid directory to create index file.")   
    if options.productName != "modeler" and options.productName != "stats":  
        parser.error("Please input valid product name modeler or stats (casesensitive) for your index file")  
    
    downloadFile(options.spedir,options.outdir, options.productName)
    
