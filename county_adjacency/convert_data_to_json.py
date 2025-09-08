#!/usr/bin/env python

import codecs

def convert_full_county_name(full_county_name):
    '''
    convert "Blah County, XY" to "XY Blah"
            "Blah Parish, LA" to "LA Blah"
            "District of Columbia, CA" to "DC District of Columbia"
    '''

    state = full_county_name[-2:]
    if state == "LA":
        return ( 'LA ' + 
            full_county_name.replace(" Parish","")[0:-4])
    elif state == "AK":
        return ( 'AK ' + 
            full_county_name.replace(" City and Borough","") 
                 .replace(" Census Area","") 
                 .replace(" Municipality","") 
                 .replace(" Borough","")[0:-4] )
    else:
        return ( state + ' ' + 
                 full_county_name.replace(" County","")[0:-4])
    
def process_lines(lines,outfile,comma=True):

    line_parts = lines[0].split('\t')

    # [1:-1] strips initial and trailing " marks
    
    state_and_county = convert_full_county_name(line_parts[0][1:-1])
    neighbor = convert_full_county_name(line_parts[2][1:-1])

    output = ""
    output += '"' + state_and_county + '" : [\n'

    # write out first neighbor 

    output += '   "' + neighbor + '"'
    if (len(lines) > 1):
        output += ',\n'
    else:
        output += '\n'
    
    # write out rest of the neighbors
    
    for i in range(1,len(lines)):

        line_parts = lines[i].split('\t')
        neighbor = convert_full_county_name(line_parts[2][1:-1])

        output += '   "' + neighbor + '"'
        if (i < len(lines)-1):
            output += ',\n'
        else:
            output += '\n'

    output += '  ]'

    if comma:
        output += ','
        
    output += '\n'
    
    outfile.write(output)
    return

def main():

    # read contents of the county adjacency file

    with codecs.open("county_adjacency.txt","r","iso-8859-1") as infile, \
         codecs.open("county_adjacency.json","w","utf-8") as outfile:
         

        outfile.write('{\n')
        
        all_lines = infile.readlines()

        start_idx = 0;
        end_idx = 1;

        while (start_idx < len(all_lines)):

            while (end_idx < len(all_lines) and
                   all_lines[end_idx][0]=='\t'):
               end_idx += 1

            process_lines(all_lines[start_idx:end_idx],
                          outfile,
                          end_idx < len(all_lines))

            start_idx = end_idx
            end_idx = start_idx + 1

        outfile.write('}\n')     
    return

if __name__=="__main__":
    main()
