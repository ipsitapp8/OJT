# os to access files and re is an enhanced version to deal with file contents. 
import os,re 

# Extracting links from the .md files. 
def extract_links(content): 
    return re.findall(r'\[.*?\]\((.*?)\)', content) 

#returning list of links.
# Extracting headings from the .md files. 
def extract_headings(content): 
    return [line for line in content.split("\n") if line.startswith("#")] 

# Creating the collection of links and headings of the opened .md file.
def parse_all_notes(folder):  
    notes = {} 
    all_files=[] 
    all_links=[] 
    for filename in os.listdir(folder): 
        if filename.endswith(".md"): 
            with open(os.path.join(folder, filename)) as f: content = f.read() 
            notes[filename] = { "content": content, "links": extract_links(content), "headings": extract_headings(content) }
            all_files.append(filename)
            all_links.extend(notes[filename]["links"]) 
    # Marking orphaned links 
    def orphan_links(): 
        orphan =set(all_files)-set(all_links) 
        return list(orphan) 
    # Marking Broken links 
    def broken_links(): 
        broken=set(all_links)-set(all_files) 
        return list(broken) 
    # Hub score 
    def Freq_outgoingLinks(): 
        #Frequency of outgoing links 
        hub_score={} 
        for filename in os.listdir(folder): 
            if filename.endswith(".md"): 
                hub_score[filename]=len(notes[filename]["links"]) 
        return hub_score