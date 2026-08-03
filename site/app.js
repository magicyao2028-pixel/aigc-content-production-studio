const workflowSteps = [
  ["Validate brief","Facts, constraints and formats"],
  ["Plan strategy","Objective, audience and message"],
  ["Build tasks","Video, image and voice"],
  ["Create manifest","Stable IDs and evidence"],
  ["Attach gates","Human approval before release"]
];

const deliverables = [
  {type:"Short video",id:"CMP-TEA-001-01-SHORT_VIDEO",ratio:"9:16",duration:"15 seconds",summary:"Three-beat hook, fact demonstration and CTA plan with product-consistency and action-continuity checks."},
  {type:"Cover image",id:"CMP-TEA-001-02-COVER_IMAGE",ratio:"9:16",duration:"Static",summary:"Mobile-first product cover with one focal object, reserved headline space and claim-compliance constraints."},
  {type:"Voiceover",id:"CMP-TEA-001-03-VOICEOVER",ratio:"Audio",duration:"15 seconds",summary:"Natural warm commercial read with timing, pronunciation, claim-accuracy and voice-rights checks."}
];

const gates = [
  ["FACTS","Product / Operations"],
  ["BRAND","Content Lead"],
  ["CLAIMS","Business Owner"],
  ["RIGHTS & PRIVACY","Content Lead"],
  ["FINAL RELEASE","Authorized Human"]
];

const trace = [
  ["validate_brief","Validate product facts, constraints and deliverable specifications."],
  ["plan_content_strategy","Translate the business objective into a content direction."],
  ["build_multimodal_tasks","Create provider-neutral image, video and voice production tasks."],
  ["create_asset_manifest","Assign stable IDs and expected evidence to planned assets."],
  ["attach_review_gates","Require factual, brand, rights, privacy and final human review."]
];

function renderPackage() {
  document.getElementById("workflow-steps").innerHTML = workflowSteps.map(([title,detail],index) => `
    <article class="workflow-step"><span>${index+1}</span><h3>${title}</h3><p>${detail}</p></article>`).join("");
  document.getElementById("deliverable-list").innerHTML = deliverables.map(item => `
    <article class="deliverable-card">
      <div class="deliverable-head"><span class="type">${item.type}</span><span class="asset-id">${item.id}</span></div>
      <h3>${item.summary.split(" with ")[0]}</h3>
      <p>${item.summary}</p>
      <div class="specs"><span>${item.ratio}</span><span>${item.duration}</span><span>Provider-neutral</span></div>
      <div class="approval">Human approval required · status: planned</div>
    </article>`).join("");
  document.getElementById("gate-list").innerHTML = gates.map(([gate,owner]) => `
    <article class="gate"><strong>${gate}</strong><span>Owner: ${owner}<br>Required before external release</span></article>`).join("");
  document.getElementById("trace-list").innerHTML = trace.map(([tool,purpose]) => `<li><strong>${tool}</strong> — ${purpose} <small>(completed)</small></li>`).join("");
  document.getElementById("run-status").textContent = "Planned · not generated";
}

document.getElementById("build-button").addEventListener("click", renderPackage);
renderPackage();
