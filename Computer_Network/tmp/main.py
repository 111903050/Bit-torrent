import sys, os
import requests
from trackers import *
from peers import *


#it reads torrent file and decodes it to the binary file
def read_torrent(file_name):
    fb = open(file_name, 'rb')
    raw_data = fb.read()
    #decoding a torrent file 
    torrent_data = bencode.decode(raw_data)
    return torrent_data
    
#to get announce list
def announce_list(torrent_data):
    try:
    #this is an extention to the official specification, offering backwards-compatibility. (list of lists of strings). 
        temp = torrent_data['announce-list']
        return temp
    except:
    #The announce URL of the tracker (string)
        return torrent_data['announce']
   



def main():
    try:
        filename = sys.argv[1]
    except:
        print('Usage: ./filename.py  torrent_filename')
        return 
    else:
        
        
        torrent_data = read_torrent(filename)          
        trackers = announce_list(torrent_data)     
        info_hash = get_info_hash(torrent_data)
        file_size = get_file_size(torrent_data)
        piece_size = torrent_data['info']['piece length']
        packet_hashes = str()
        packet_hashes = bytearray(packet_hashes, 'utf-8') + binascii.unhexlify(info_hash)
        
        piece_count = get_piece_count(torrent_data, file_size)
        
        block_count = int(torrent_data['info']['piece length']/2**14)
        
        pwd = os.getcwd()
        try:
            torrent_data['info']['files']
        except KeyError:
            try:
                sys.argv[2]
            except:
                file = pwd + '/' + torrent_data['info']['name']
            else:
                file = pwd + '/' + sys.argv[2] + '/' + file
            nikhil = open(file, 'wb+')
            print('File_Name: ', torrent_data['info']['name'], '\nFile_size: ', torrent_data['info']['length'], 'bytes')
        else:
            print('Directory_Name: ', torrent_data['info']['name'])
            for i in range(len(torrent_data['info']['files'][0])):
                print('File_Name: ', torrent_data['info']['files'][i]['path'][0], '\nFile_size: ', torrent_data['info']['files'][i]['length'], 'bytes')
            nikhil = open('temporary', 'wb+')

        print('Info_hash: ', info_hash)
        print('No. of Pieces: ', piece_count)
        print('Piece Size: ', piece_size, 'bytes\n')
        if type(trackers) == list:
            trackers_list = []
            for i in trackers:
                for j in i:
                    trackers_list.append(j)
        else:
            trackers_list = [trackers]
            
        
        list_of_working_tracker =  get_working_trackers(trackers_list)
        
        total_peers = []
        print(list_of_working_tracker)
        for tracker in list_of_working_tracker:
            if tracker[0] == 'udp':
                try:
                    peer_ids = udp_connection(tracker, info_hash, file_size)
                    print(peer_ids)
                    if peer_ids == 'announce_timeout' or peer_ids == 'connection_timeout' or peer_ids == 'scrape_timeout':
                        print('timed_out: poor network connection', peer_ids)
                        continue
                    total_peers = total_peers + peer_ids
                except:
                    pass
            elif tracker[0] == 'http':
                print("yes")
                try:
                    peer_ids = http_connection(tracker, info_hash, file_size)
                    print(peer_ids)
                    if peer_ids == 'timed_out':
                        print('timed_out: poor network connection')
                        continue
                    total_peers = total_peers + peer_ids
        
                except:
                    pass
            elif tracker[0] == 'https':
                try:
                    peer_ids = https_connection(tracker, info_hash, file_size)
                    if peer_ids == 'timed_out':
                        print('timed_out: poor network connection')
                        continue
                    total_peers = total_peers + peer_ids
        
                except:
                    pass
        print("Got", len(total_peers), "peers from all trackers", total_peers, '\n')
        print("success")
        
if __name__ == '__main__':
  main()
