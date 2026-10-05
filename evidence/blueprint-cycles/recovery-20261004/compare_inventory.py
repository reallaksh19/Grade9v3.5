import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
inventory=json.loads((root/"evidence/blueprint-cycles/pending-compatibility-upload.json").read_text(encoding="utf-8"))
rows=[]
for item in inventory["pending_files"]:
    path=root/item["path"]
    if not path.is_file():
        rows.append({"path":item["path"],"status":"MISSING","expected_sha256":item["sha256"]})
        continue
    data=path.read_bytes()
    observed=hashlib.sha256(data).hexdigest()
    blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    rows.append({"path":item["path"],"status":"MATCH" if observed==item["sha256"] and blob==item["git_blob_sha"] else "DIFFERENT","expected_sha256":item["sha256"],"actual_sha256":observed,"expected_git_blob":item["git_blob_sha"],"actual_git_blob":blob})
report={"schema":"issue29-recovery-inventory/v1","material_head":subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip(),"historical_artifact_basis":inventory["published_snapshot_commit"],"source":"pending-compatibility-upload.json","counts":{s:sum(r["status"]==s for r in rows) for s in ["MATCH","DIFFERENT","MISSING"]},"files":rows,"claim":"Comparison against published current-head bytes, not proof of recovered historical local files."}
(out/"pending-inventory-comparison.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report["counts"]))

