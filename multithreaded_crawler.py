from urllib.request import Request, urlopen, URLError, urljoin
from urllib.parse import urlparse
import time
import threading
import queue
from bs4 import BeautifulSoup
import ssl

class Crawler(threading.Thread):
    def __init__(self,base_url, links_to_crawl,have_visited, error_links,url_lock):
       
        threading.Thread.__init__(self)
        print(f"Web Crawler worker {threading.current_thread()} has Started")
        self.base_url = base_url
        self.links_to_crawl = links_to_crawl
        self.have_visited = have_visited
        self.error_links = error_links
        self.url_lock = url_lock

    def run(self):
        # we create a ssl context so that our script can crawl
        # the https sties with ssl_handshake.

        #Create a SSLContext object with default settings.
        my_ssl = ssl.create_default_context()

        # by default when creating a default ssl context and making an handshake
        # we verify the hostname with the certificate but our objective is to crawl
        # the webpage so we will not be checking the validity of the cerfificate.
        my_ssl.check_hostname = False

        # in this case we are not verifying the certificate and any 
        # certificate is accepted in this mode.
        my_ssl.verify_mode = ssl.CERT_NONE

        # we are defining an infinite while loop so that all the links in our
        # queue are processed.

        while True:

            # In this part of the code we create a global lock on our queue of 
            # links so that no two threads can access the queue at same time
            self.url_lock.acquire()
            print(f"Queue Size: {self.links_to_crawl.qsize()}")
            link = self.links_to_crawl.get()
            self.url_lock.release()

            # if the link is None the queue is exhausted or the threads are yet
            # process the links.

            if link is None:
                break
            
            # if The link is already visited we break the execution.
            if link in self.have_visited:
                print(f"The link {link} is already visited")
                break

            try:
                # This method constructs a full "absolute" URL by combining the
                # base url with other url. this uses components of the base URL, 
                # in particular the addressing scheme, the network 
                # location and  the path, to provide missing components 
                # in the relative URL.
                # in short we repair our relative url if it is broken.
                link = urljoin(self.base_url,link)

                # we use the header parameter to "spoof" the "User-Agent" header
                # value which is used by the browser to identify itself. This is
                # because some servers will only allow the connection if  it comes
                # from a verified browser. In this case we are using FireFox header. 
                req = Request(link, headers= {'User-Agent': 'Mozilla/5.0'})

                # we are opening the url using a ssl handshake.
                response = urlopen(req, context=my_ssl)

                print(f"The URL {response.geturl()} crawled with \
                      status {response.getcode()}")

                # this returns the html representation of the webpage
                soup = BeautifulSoup(response.read(),"html.parser")

                # in this case we are finding all the links in the page.
                for a_tag in soup.find_all('a'):
                    # we are checking of the link is already visited and (network location part) is our
                    # base url itself.
                    if (a_tag.get("href") not in self.have_visited) and (urlparse(link).netloc == "www.python.org"):
                        self.links_to_crawl.put(a_tag.get("href"))
                    
                    else:
                        print(f"The link {a_tag.get('href')} is already visited or is not part \
                        of the website")

                print(f"Adding {link} to the crawled list")
                self.have_visited.add(link)

            except URLError as e:
                print(f"URL {link} threw this error {e.reason} while trying to parse")

                self.error_links.append(link)

            finally:
                self.links_to_crawl.task_done()

print("The Crawler is started")
base_url = input("Please Enter Website to Crawl > ")
number_of_threads = input("Please Enter number of Threads > ")

links_to_crawl = queue.Queue()
url_lock = threading.Lock()
links_to_crawl.put(base_url)

have_visited = set()
crawler_threads = []
error_links = []
#base_url, links_to_crawl,have_visited, error_links,url_lock
for i in range(int(number_of_threads)):
    crawler = Crawler(base_url = base_url, 
                      links_to_crawl= links_to_crawl, 
                      have_visited= have_visited,
                      error_links= error_links,
                      url_lock=url_lock)
    
    crawler.start()
    crawler_threads.append(crawler)


for crawler in crawler_threads:
    crawler.join()



print(f"Total Number of pages visited are {len(have_visited)}")
print(f"Total Number of Errornous links: {len(error_links)}")


                



