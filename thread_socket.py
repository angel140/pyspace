# -*- coding: utf-8 -*-  
import socket
import sys
import threading 
from time import ctime 
import select
import queue
import time

class NoResultsPending(Exception):
    """All works requests have been processed"""
    pass

class NoWorkersAvailable(Exception):
    """No worket threads available to process remaining requests."""
    pass
 
def _handle_thread_exception(request, exc_info):
    """默认的异常处理函数，只是简单的打印"""
    traceback.print_exception(*exc_info)

class WorkRequest:
    '''
    @param callable_:，可定制的，执行work的函数
    @param args: 列表参数
    @param kwds: 字典参数
    @param requestID: id
    @param callback: 可定制的，处理resultQueue队列元素的函数
    @param exc_callback:可定制的，处理异常的函数 
    '''
    def __init__(self,priority,callable_,args=None,kwds=None,requestID=None,
                 callback=None,exc_callback=_handle_thread_exception):
        if requestID == None:
            self.requestID = id(self)
        else:
            try:
                self.requestID = hash(requestID)
            except TypeError:
                raise TypeError("requestId must be hashable")  
        self.priority = priority  
        self.exception = False
        self.callback = callback
        self.exc_callback = exc_callback
        self.callable = callable_
        self.args = args or []
        self.kwds = kwds or {}

    def __lt__(self, other):
        if self.priority < other.priority:
            return True
        else:
            return False
        
    def __str__(self):
        return "WorkRequest id=%s args=%r kwargs=%r exception=%s" % \
            (self.requestID,self.args,self.kwds,self.exception) 



class WorkerThread(threading.Thread):
    """后台线程，真正的工作线程，从请求队列(requestQueue)中获取work，
    并将执行后的结果添加到结果队列(resultQueue)"""
    def __init__(self,requestQueue,resultQueue,poll_timeout=5,**kwds):
        threading.Thread.__init__(self,**kwds)
        '''设置为守护进行'''
        self.setDaemon(True)
        self._requestQueue = requestQueue
        self._resultQueue = resultQueue
        self._poll_timeout = poll_timeout
        '''设置一个flag信号，用来表示该线程是否还被dismiss,默认为false'''
        self._dismissed = threading.Event()
        self.start()
        
    def run(self):
        '''每个线程尽可能多的执行work，所以采用loop，
        只要线程可用，并且requestQueue有work未完成，则一直loop'''
        print("run thread")
        while True:
            if self._dismissed.is_set():
                break
            try:
                '''
                Queue.Queue队列设置了线程同步策略，并且可以设置timeout。
                一直block，直到requestQueue有值，或者超时
                '''
                request = self._requestQueue.get(True,self._poll_timeout)
                result = request.callable(*request.args,**request.kwds)
                print (self.getName())
                self._resultQueue.put((request,result))
            except queue.Empty:
                print("run thread empty")
                continue
            else:
                '''之所以在这里再次判断dimissed，是因为之前的timeout时间里，很有可能，该线程被dismiss掉了'''
                if self._dismissed.is_set():
                    self._requestQueue.put(request)
                    break
                try:
                    '''执行callable，讲请求和结果以tuple的方式放入requestQueue'''
                    result = request.callable(*request.args,**request.kwds)
                    print (self.getName())
                    self._resultQueue.put((request,result))
                except:
                    '''异常处理'''
                    request.exception = True
                    self._resultQueue.put((request,sys.exc_info()))
    
    def dismiss(self):
        '''设置一个标志，表示完成当前work之后，退出'''
        self._dismissed.set()

class ThreadPool:
    '''
    @param num_workers:初始化的线程数量
    @param q_size,resq_size: requestQueue和result队列的初始大小
    @param poll_timeout: 设置工作线程WorkerThread的timeout，也就是等待requestQueue的timeout
    '''
    def __init__(self,num_workers,q_size=0,resq_size=0,poll_timeout=5):
        self._requestQueue = queue.PriorityQueue(q_size)
        self._resultQueue = queue.Queue(resq_size)
        self.workers = []
        self.dismissedWorkers = []
        self.workRequests = {} #设置个字典，方便使用
        self.createWorkers(num_workers,poll_timeout)

    def createWorkers(self,num_workers,poll_timeout=5):
        '''创建num_workers个WorkThread,默认timeout为5'''
        for i in range(num_workers):
            self.workers.append(WorkerThread(self._requestQueue,self._resultQueue,poll_timeout=poll_timeout))                           
    
    def dismissWorkers(self,num_workers,do_join=False):
        '''停用num_workers数量的线程，并加入dismiss_list'''
        dismiss_list = []
        for i in range(min(num_workers,len(self.workers))):
            worker = self.workers.pop()
            worker.dismiss()
            dismiss_list.append(worker)
        if do_join :
            for worker in dismiss_list:
                worker.join()
        else:
            self.dismissedWorkers.extend(dismiss_list)
    
    def joinAllDismissedWorkers(self):
        '''join 所有停用的thread'''
        #print len(self.dismissedWorkers)
        for worker in self.dismissedWorkers:
            worker.join()
        self.dismissedWorkers = []
    
    def putRequest(self,request ,block=True,timeout=None):
        assert isinstance(request,WorkRequest)
        assert not getattr(request,'exception',None)
        '''当queue满了，也就是容量达到了前面设定的q_size,它将一直阻塞，直到有空余位置，或是timeout'''
        self._requestQueue.put(request, block, timeout)
        self.workRequests[request.requestID] = request
        
    def poll(self,block = False):
        while True:
            if not self.workRequests:
                raise NoResultsPending
            elif block and not self.workers:
                raise NoWorkersAvailable
            try:
                '''默认只要resultQueue有值，则取出，否则一直block'''
                request , result = self._resultQueue.get(block=block)
                if request.exception and request.exc_callback:
                    request.exc_callback(request,result)
                if request.callback and not (request.exception and request.exc_callback):
                    request.callback(request,result)
                del self.workRequests[request.requestID]
            except queue.Empty:
                break
    
    def wait(self):
        while True:
            try:
                self.poll(True)
            except NoResultsPending:
                break
    
    def workersize(self):
        return len(self.workers)
    
    def stop(self):
        '''join 所有的thread,确保所有的线程都执行完毕'''
        self.dismissWorkers(self.workersize(),True)
        self.joinAllDismissedWorkers()


HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except (socket.error , msg):
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print ('Socket bind complete')
 
#Start listening on socket
s.listen(10)
print ('Socket now listening')
 
#Function for handling connections. This will be used to create threads
def clientthread(*args,**kwds):
    #Sending message to connected client

    #infinite loop so that function do not terminate and thread do not end.
    #while True:
         
        #Receiving from client
    conn = kwds['conncet']
    data = conn.recv(1024)
    #if not data: 
    #    break
     
    conn.send(('[%s] %s' % (ctime(), data)).encode())
     
    #came out of loop


def print_result(request,result):
    print ("---Result from request %s : %r" % (request.requestID,result))

outputs = []
inputs = [s]
clientmap = {}


main_pool = ThreadPool(3)
#now keep talking with the client
while 1:

    #wait to accept a connection - blocking call
    try:
        readable,writeable,exceptional = select.select(inputs,outputs,[])
        #此处会被select模块阻塞，只有当监听的三个参数发生变化时，select才会返回
    except select.error:
        break

    if s in readable:
        conn, addr = s.accept()
        print ('Connected with ' + addr[0] + ':' + str(addr[1]))
        outputs.append(conn)
        clientmap[conn]=addr
        inputs.append(conn)

    elif len(readable) != 0:
        #1, 取出这个列表中的socket
        csock=readable[0]
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        
        req = WorkRequest(1,clientthread,args=[],kwds={'conncet': csock },callback=print_result)
        main_pool.putRequest(req)
        print("put a request")

        
 
s.close()