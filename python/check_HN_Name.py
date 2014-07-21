#!/
class check_HN_name:
    def init(self): 
        pass
    
    def stdaloneCheck(self):  
 
        import urllib
        import commands
        import os
        print 'start standalone check ...\n'
        # direct stderr from voms-proxy-* to dev/null to avoid stupid Java messages :-(
        status, dn = commands.getstatusoutput('eval `scram unsetenv -sh`; voms-proxy-info -identity 2>/dev/null')
        if status == 0:
           print "my DN is: %s \n"%dn
        status, proxyFile = commands.getstatusoutput('eval `scram unsetenv -sh`; voms-proxy-info -path 2>/dev/null')
        if not status == 0:
            print 'ERROR getting proxy path'
        os.environ['X509_USER_PROXY'] = proxyFile
        if not 'X509_CERT_DIR' in os.environ:
            os.environ['X509_CERT_DIR'] = '/etc/grid-security/certificates'

        cmd = "curl -s  --capath $X509_CERT_DIR --cert $X509_USER_PROXY --key $X509_USER_PROXY 'https://cmsweb.cern.ch/sitedb/data/prod/whoami'|tr ':,' '\n'|grep -A1 login|tail -1"

        status, username = commands.getstatusoutput(cmd)
        
        print 'my HN user name is: %s' % username
        print '\nend check.....................'

    def crabCheck(self):
        from CrabLogger import CrabLogger
        from WorkSpace import WorkSpace, common
        import tempfile, urllib, os, string
      
        dname = tempfile.mkdtemp( "", "crab_", '/tmp' )
        os.system("mkdir %s/log"%dname )
        os.system("touch %s/crab.log"%dname )
        
        cfg_params={'USER.logdir' : dname }
        common.work_space = WorkSpace(dname, cfg_params)
        args = string.join(sys.argv,' ')
        common.debugLevel = 0
        common.logger = CrabLogger(args)
        
        from crab_util import getDN,gethnUserNameFromSiteDB
        print 'start using CRAB utils ...\n'
        print "my DN is: %s \n"%getDN()
        try:
            print 'my HN user name is: %s \n'%gethnUserNameFromSiteDB()
        except:
            print '\nWARNING native crab_utils failed! ' 
            dn=urllib.urlencode({'dn':getDN()})
            print 'trying now using urlencoded DN: \n\t %s '%dn
            status,hnName = self.gethnName_urlenc(dn)
            if status == 1: 
                print '\nWARNING: failed also using urlencoded DN '
            else: 
                print 'my HN user name is: %s \n'%hnName
                print 'problems with crab_utils'   
        print '\nend check.....................'
        
        os.system("rm -rf %s"%dname )
         
    def gethnName_urlenc(self,dn):
        from WMCore.Services.SiteDB.SiteDB import SiteDBJSON
        hnUserName = None
        userdn = dn
        mySiteDB = SiteDBJSON()
        status = 0 
        try:
            hnUserName = mySiteDB.dnUserName(dn=userdn)
        except:
            status = 1 
        return status,hnUserName


if __name__ == '__main__' :
    import sys
    args = sys.argv[1:]
    check = check_HN_name()

    if 'crab' in args:
        check.crabCheck()  
    else:
        check.stdaloneCheck()  

