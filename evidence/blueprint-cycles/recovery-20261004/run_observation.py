import argparse,datetime,json,os,re,subprocess,sys,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--repo",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
p.add_argument("--name",required=True)
p.add_argument("command",nargs=argparse.REMAINDER)
a=p.parse_args()
cmd=a.command[1:] if a.command[:1]==["--"] else a.command
a.out.mkdir(parents=True,exist_ok=True)
env={**os.environ,"PYTHONUTF8":"1","PYTHONIOENCODING":"utf-8"}
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
t=time.monotonic()
log=a.out/(a.name+".log")
with log.open("w",encoding="utf-8",newline="\n") as stream:
    proc=subprocess.run(cmd,cwd=a.repo,env=env,stdout=stream,stderr=subprocess.STDOUT)
content=log.read_text(encoding="utf-8")
head=subprocess.check_output(["git","-C",str(a.repo),"rev-parse","HEAD"],text=True).strip()
failures=re.findall(r"^(?:FAIL|ERROR): (.+)$",content,re.M)
summary={"name":a.name,"command":cmd,"cwd":str(a.repo.resolve()),"basis_head":head,"started_utc":start,"seconds":round(time.monotonic()-t,3),"exit_code":proc.returncode,"failures":failures,"log":log.name,"tests_summary":re.findall(r"^(?:Ran \d+ tests? in .+|OK.*|FAILED .*)$",content,re.M)}
(a.out/(a.name+".json")).write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary))
print("\n".join(content.splitlines()[-12:]))
raise SystemExit(proc.returncode)

