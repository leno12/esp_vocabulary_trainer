#!/bin/python
import json
import os
import sys
import subprocess as sp
from multiprocessing import Pool
import shutil as sh
from glob import glob
from copy import copy
import difflib
import pexpect as px
import yaml
import re
import diff_match_patch as dmp_lib

#TODO Worker pool returns list, not directory
#TODO get better linter
#TODO make testcase generatorscript!
#TODO make pretty testreport generator
#TODO flag for pretty print, and run parallel 
#TODO refactor 
#TODO fix Input and output in one line !!! (Input format, if requested)
#TODO add local variables for stack (vars?) for tags
#TODO create folders results and tmp if not existing
magic_char = '\b' #Indicates a special input line mixed with output and input

def pointer_align(x):
    # stupid hack to get rid of * alginment differences
    x = x.strip()
    if "*" in x:
        i = x.rsplit("*", 1)
        i[0] += "*"
        x = " ".join(list(map(lambda x:x.replace(" ", ""),i))).strip()
    return x

def get_blank_result():
    retvar = {
                "implemented":False,
                "diff":[],
                "passed":False,
                "timeout":False,
                "output":"",
                "valgrind":{"errors":0,"contexts":0},
                "score":0.0
            }
    return retvar
def parse_prototype(p):

    n,paras = p.split("(")
    paras = paras.replace(")","").split(",")
    n = n.split("         ")[-1].split(" ")
    name = n.pop(-1).strip()
    r = " ".join(n)
    paras = list(map(lambda x: x.rsplit(" ",1)[0].strip() if "[]" not in x else x.rsplit(" ")[0].strip()+"[]",paras))
    paras = list(map(lambda x: pointer_align(x),paras))
    return r, name, paras


class assignment_checker:
    def __init__(self, desc):
        self.log = {}
        self.desc = desc
        self.run_parallel = False
        self.assignment_root = desc["compinfo"]["assignment_root"]
        self.not_implemented = []

    def build(self):
        self.log["builds"] = True
        try:
            sp.check_call(["make", "all"], cwd=self.assignment_root)
        except Exception:
            print("cannot compile")
            self.log["builds"] = False
        return self.log["builds"]

    def get_functions(self):
        retvar = []
        for f in self.desc["compinfo"]["codefiles"]:
            tags = sp.check_output(
                ["ctags", "-x", "--c-kinds=fp", f],
                cwd=self.assignment_root).decode("utf-8").splitlines()
            #filter out prototype declarations
            tags = list(filter(lambda x: "function" in x,tags))
            retvar += list(map(lambda x: x.split("           ")[-1], tags))
        return retvar

    def get_testcases(self):
        testcases = []
        self.fcts = list(map(lambda x:parse_prototype(x) ,self.get_functions()))
        for tc in self.desc["testcases"]:
            if("mode" in tc and tc["mode"] == "unit"):
                # if testcase is defined as unit test check if this signature is implemented
                intypes = list(map(lambda x : x.strip(),tc["tags"]["<INTYPES>"].split(",")))
                fname = tc["tags"]["<FNAME>"].strip()
                rettype = tc["tags"]["<RETTYPE>"].strip()
                
                signature = (rettype,fname,intypes)
                if(signature in self.fcts):
                    testcases.append(copy(tc))
                else:
                    self.not_implemented.append(copy(tc))
            else:
                testcases.append(copy(tc))
        return testcases


    def go(self):
        results = {}
        if self.build():
            runners = []
            lib = self.desc["compinfo"]["libfile"]
            binary = self.desc["compinfo"]["binary"]
            #create a list of all runners
            for i,tc in enumerate(self.get_testcases()):
                runners.append(tc_runner(lib,tc,"./tmp/{}".format(i),binary))

            vgouts = {}
            if self.run_parallel == True:
                p = Pool()
                results = p.map(tc_runner.run,runners)
            else:
                for r in runners:
                    result,vgout = r.run()
                    result["implemented"] = True
                    results[r.name] = result
                    vgouts[r.name]=vgout
            #dont forget the not implemented testcases
            for no_impl in self.not_implemented:
                not_impl_res = get_blank_result()
                results[no_impl["name"]]=not_impl_res
        results["log"] = self.log
        return results

class tc_runner:
    def __init__(self,lib,desc,cwd,binary):
        self.desc = desc
        self.vg_out = ""
        self.out = ""
        self.result = {}
        self.lib = lib
        self.name = desc["name"]
        self.timeout = 60
        self.cwd = cwd
        self.cmd = binary
        self.vgfile = self.cwd+"/vglog.txt"
        if "args" in self.desc:
            self.args = self.desc["args"]
        else:
            self.args = ""
        self.result["diff"] = []
        self.result["passed"] = False
        self.result["timeout"] = False #TODO measure timestamp
        self.result["output"]=""
        self.result["valgrind"]={"errors":0,"contexts":0}
        self.score = 0.0
        if "timeout" in desc:
            self.timeout = str(desc["timeout"])

    def replace_tags(self):
        #replace all tags in ALL files in ./tmp
        for path in glob(self.cwd+"/*"):
            with open(path,"r+") as f:
                cont = f.read()
                for repl in self.desc["tags"]:
                    if repl == "<LIBRARY>" and self.desc["tags"][repl] == "":
                        cont = cont.replace(repl, self.lib)
                    elif repl == "<SETUPCODE>":
                        #TODO proper identation
                        index = cont.find(repl)
                        if index != -1:
                            cont = cont.replace(repl,self.desc["tags"][repl])
                            #cont = cont[:index-len(repl)] + self.desc["tags"][repl] + cont [index+len(repl):]

                    else:
                        cont = cont.replace(repl, self.desc["tags"][repl])
                #cleanup if neccessary
                if "<SETUPCODE>" in cont:
                    cont = cont.replace("<SETUPCODE>","")
                f.seek(0)
                f.write(cont)
                f.truncate()

    def build_unit_test(self):
        sh.copytree("./template",self.cwd)
        self.replace_tags()
        rvar = sp.call(["make"],cwd=self.cwd)
        print(rvar)

    def run_as_full_testcase(self,cmd):
        child = px.spawn("valgrind --leak-check=full --log-file={} {} {}".format(self.vgfile,cmd,self.args),
        cwd=os.path.abspath("."),timeout=self.timeout)
        self.result["passed"]=False
        outcounter = 0
        passedcounter = 0
        self.result["passed"] = True
        for i,line in enumerate(self.desc["io"]):
            if(line[0] != ""):
                child.sendline(line[0])
                #input is echoed back so, i need to expect it
                child.expect(["\r\n"])

            outputlines = line[1].splitlines()
            for idx,out in enumerate(outputlines):
                outcounter += 1
                try:    
                    child.expect(["\r\n"])
                    outp = child.before.decode("utf-8").strip()
                    self.result["output"]+="{}:>>{}\n<<{}\n".format(i,line[0],outp)
                    diff,lev = make_diff(out.strip(),outp)
                    self.result["diff"].append(diff)
                    if(lev==0):
                        passedcounter+=1
                    else:
                        self.result["passed"] = False
                except px.TIMEOUT:
                    self.result["timeout"]=True
                    self.result["passed"] = False
                    break

                except px.EOF:
                    print("process died")
                    self.result["passed"] = False
                    break
            self.result["score"] = passedcounter/outcounter

    def get_valgrind_output(self):
        with open(self.vgfile) as f :
            m = re.match(r"==\d+== ERROR SUMMARY: (\d+) \D+(\d+)",f.readlines()[-1]).groups()
            self.result["valgrind"]={"errors":int(m[0]),"contexts":int(m[1])}

    def run_as_unit_test(self,cmd):
        try:
            outp = sp.check_output(["valgrind","--leak-check=full","--log-file=vglog.txt","./"+cmd,self.args],
            cwd=self.cwd,
            timeout=self.timeout).decode("utf-8")
            diff,lev = make_diff(outp.strip(),self.desc["result"])
            self.result["output"] = outp
            self.result["diff"] = [diff]
            if(lev == 0):
                self.result["passed"] = True
        except sp.TimeoutExpired:
            self.result["timeout"] = True
        except:
            print("unknown expection" ,sys.exc_info())
        if(self.result["passed"]):
            self.result["score"]=1.0
        else:
            self.result["score"]=0.0

    def run_as_full_io(self,cmd):
        #self.result = get_blank_result()
        infile = self.desc["infile"]
        self.result["passed"] = False
        self.result["score"]=0.0
        self.result["diff"]= []
        outp = ""
        res = self.desc["result"]
        with open(infile) as f:
            inp = f.read()
            child = px.spawn("valgrind --leak-check=full --log-file={} {} {}".format(self.vgfile,cmd,self.args),
            cwd=os.path.abspath("."),timeout=5,maxread=1)
            child.send(inp)
            child.expect(inp.replace("\n","\r\n"))
            try:
                child.expect(px.EOF)
                outp = child.before.decode("utf-8").replace("\r","")
                o = "\n".join(list(map(lambda x: x.strip(),outp.splitlines())))
                r = "\n".join(list(map(lambda x: x.strip(),res.splitlines())))
                diff ,lev = make_diff(r,o)
                self.result["diff"] = [diff] 
                if(lev == 0):
                    self.result["passed"] = True
                    self.result["score"] = 1.0
            except px.TIMEOUT:
                self.result["timeout"]=True
            #diff = make_diff()
    def run(self):
        try:
            if "mode" in self.desc and self.desc["mode"]=="unit":
                self.build_unit_test()
                cmd = "a.out"
                self.run_as_unit_test(cmd)
            elif "mode" in self.desc and self.desc["mode"]=="full":
                os.mkdir(self.cwd)
                self.run_as_full_testcase(self.cmd)
            elif "mode" in self.desc and self.desc["mode"]=="io":
                os.mkdir(self.cwd)
                self.run_as_full_io(self.cmd)
            self.get_valgrind_output()
        except:
            #process died somehow, testcase failed
            print("testcase died")
            self.result = get_blank_result()
            self.result["exception"] = sys.exc_info()
        return self.result,self.vg_out

def make_diff(string1,string2):
    dmp = dmp_lib.diff_match_patch()
    diff = dmp.diff_main(string2,string1)
    return json.dumps(diff),dmp.diff_levenshtein(diff)

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except:
        filename = "./test_definition/testdef.yml"
    
    files = glob('./tmp/*')
    for f in files:
        sh.rmtree(f)

    with open(filename) as f:
        try:
            desc = yaml.load(f.read(),Loader=yaml.FullLoader)
        except:
            print("Cannot load the test description \n",sys.exc_info())
            exit()
        try:
            ac = assignment_checker(desc)
            results = ac.go()
        except KeyError:
            print("Missed some keys in the description json?")
            print(sys.exc_info())

    with open("./results/results.json","w") as f:
        json.dump(results,f)
