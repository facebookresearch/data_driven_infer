/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 * 
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

const fs = require('fs');
const fmt = require('./formating.js');

const table = {};

const set = new Set();
const mlset = new Set();
const baseset = new Set();
const reports = {};

let name;
let md_mode = false;
let terminal_mode = false;
let ml_mode = false
let group_mode = false;
let summary_mode = false;
let filter_memory = false;
let similarity_mode = false;
let similarity2_mode = false;
let no_endline = false;
const files = [];
for (let i=2; i<process.argv.length; i++) {
	let filename = process.argv[i];
	if (filename.startsWith("-")) {
		if (filename === '-md') md_mode = true;
		if (filename === '-tm') terminal_mode = true;
		if (filename === '-g') group_mode = true;
		if (filename === '-s') summary_mode = true;
		if (filename === '-a') similarity_mode = true;
		if (filename === '-a2') similarity2_mode = true;
		if (filename === '-fm') filter_memory = true;
		if (filename === '-e') no_endline = true;
		continue;
	}
	files.push(filename);
}
files.sort((x, y) => {
	let xx = x.replace('.json', '').replace(/.*\//, '').split('_');
	let yy = y.replace('.json', '').replace(/.*\//, '').split('_');
	if (xx[2] !== undefined && yy[2] !== undefined) {
		return ((+xx[1]) > (+yy[1]))?1: -1;
	} else {
		if (xx[2] !== undefined) return 1;
		if (yy[2] !== undefined) return -1;
		if ((+xx[1]) === (+yy[1])) return 0;
		return ((+xx[1]) > (+yy[1]))?1: -1;
	}
});
let hash;
if (group_mode) {
	hash = function (obj) {
		if (obj.bug_type === "STACK_VARIABLE_ADDRESS_ESCAPE") {
			obj = { bug_type: obj.bug_type,
				trace: obj.bug_trace[0] };
		} else {
			obj = { bug_type: obj.bug_type,
				trace: obj.bug_trace[1].description };
		}
		return JSON.stringify(obj);
	}
} else {
	hash = function (obj) {
		return JSON.stringify(obj);
	}
}

function get_similarity_hash(hash) {
	return JSON.stringify(JSON.parse(hash).bug_trace[0]);
}

let ml_new = -1;
for (let i=0; i<files.length; i++) {
	let filename = files[i];
	let uname = filename.replace('.json', '');
	let txt = uname.replace(/.*\//, '').split('_');
	name = `${txt[0]}`;
	let k = +txt[1];
	if (txt[2] !== undefined) {
		ml_mode = true;
		k = k + "-" + txt[2];
		if (ml_new === -1) ml_new = set.size;
	}
	if (txt[3] !== undefined) {
		k = k + "-" + txt[3];
	}
	let raw = "[]";
	try {
		raw = fs.readFileSync(filename);
	} catch (_) {}
	const json = JSON.parse(raw);
	const items = new Set();
	for (let j=0; j<json.length; j++) {
		const uid = hash(json[j]);
		let bt = json[j].bug_type;
		if (filter_memory && bt !== 'MEMORY_LEAK') {
			continue;
		}
		if (reports[bt] === undefined) {
			reports[bt] = {};
		}
		reports[bt][uid] = true;
		set.add(uid);
		if (txt[2] === undefined) baseset.add(uid);
		else mlset.add(uid);
		items.add(uid);
	}
	table[k] = items;
}
const ml_new_total = set.size - ml_new;
if (!ml_mode) ml_new = set.size;

const alignMap = {'left': fmt.alignLeft, 'right': fmt.alignRight, 'center': fmt.alignCenter};
function markdown(o) {
	let cols = o.cols;
	o = o.data;
	// rows
	const head = [{name: "Case"}];
	for (let i=0; i<cols.length; i++) {
		head[head.length] = {name: cols[i]};
	}

	// calculate the column size
	for (let i=0; i<o.length; i++) {
		for (let j=0; j<head.length; j++) {
			let len = (""+o[i][j]).length;
			head[j].length = Math.max(head[j].length || head[j].name.length, len);
		}
	}

	// head
	let row;
	row = [];
	for (let i=0; i<head.length; i++) {
		row[i] = fmt.alignLeft(head[i].name, head[i].length);
	}
	console.log("|", row.join(" | "), "|");
	// hl
	row = [];
	let alignstr;
	for (let i=0; i<head.length; i++) {
		alignstr = head[i].align;
		if (alignstr === 'left') {
			row[i] = ':-' + '-'.repeat(head[i].length - 2);
		} else if (alignstr === 'right') {
			row[i] = '-'.repeat(head[i].length - 2) + '-:';
		} else if (alignstr === 'center') {
			row[i] = ':' + '-'.repeat(head[i].length - 2) + ':';
		} else {
			row[i] = '-'.repeat(head[i].length);
		}
	}
	console.log("|", row.join(" | "), "|");

	// body
	let align;
	for (let i=0; i<o.length; i++) {
		row = [];
		for (let j=0; j<head.length; j++) {
			align = alignMap[head[j].align || 'left'];
			row[j] = align(o[i][j], head[j].length);
		}
		console.log("|", row.join(" | "), "|");
	}
}

const marks = ["o", "-", "N"];
const keys = Object.keys(table);
keys.sort((x, y) => {
	let xx = x.split('-'), yy = y.split('-');
	let xx1 = xx[1] === undefined? 0 : 1;
	let yy1 = yy[1] === undefined? 0 : 1;
	if (xx[0] === yy[0]) return xx1-yy1;
	else return xx[0] - yy[0];
});

const color_code = "\u001b[32m";
const reset_code = "\u001b[39m";
if (md_mode) {
	const data = [], cols = [];
	set.forEach(x => cols[cols.length] = ""+cols.length );

	for (let i=0; i<keys.length; i++) {
		let items = table[keys[i]];
		let casetitle = `${name} (k = ${keys[i]})`;
		let arr = [casetitle];
		set.forEach(x => arr[arr.length] = items.has(x)? marks[0] : marks[1]);
		data[data.length] = arr;
	}

	markdown({data, cols});
} else if (terminal_mode) {
	for (let i=0; i<keys.length; i++) {
		let items = table[keys[i]];
		let out = "";
		let casetitle = `${name} (k = ${keys[i]})`;
		const len = name.length + "(k =        )".length;
		set.forEach(x => out += items.has(x)? marks[0] : marks[1]);
		if (keys[i].endsWith("-ML")) 
			process.stdout.write(color_code);
		console.log(fmt.alignLeft(casetitle, len), fmt.alignLeft(`(${items.size}/${set.size}):`, 10), out, reset_code);
	}
} else if (summary_mode && ml_mode) {
	const mlonly = new Set([...mlset].filter(x => !baseset.has(x)));
	const baseonly = new Set([...baseset].filter(x => !mlset.has(x)));
	const inter = new Set([...mlset].filter(x => baseset.has(x)));
	if (similarity_mode) {
		const basesim = [...baseset].map(get_similarity_hash);
		const mlsim = [...mlset].map(get_similarity_hash);
		const sim = [...mlsim].filter(x => basesim.indexOf(x)>=0);
		if (baseset.size+mlset.size === 0) console.log(0)
		else console.log(sim.length*2/(baseset.size+mlset.size));
	} else if (similarity2_mode) {
		const mlonlysim = [...mlonly].map(get_similarity_hash);
		const basesim = [...baseset].map(get_similarity_hash);
		const mlsim = [...mlset].map(get_similarity_hash);
		const sim = [...mlonlysim].filter(x => basesim.indexOf(x)>=0);
		const r = (inter.size+sim.length)/(mlonly.size+inter.size);
		console.log(r);
	} else {
		if (no_endline) {
			const out = `${baseset.size} ${mlset.size} ${baseonly.size} ${mlonly.size} ${inter.size} ${(inter.size*2/(baseset.size+mlset.size)).toFixed(2)}`;
			process.stdout.write(out);
		} else {
			console.log(baseset.size, mlset.size, baseonly.size, mlonly.size, inter.size, (inter.size*2/(baseset.size+mlset.size)).toFixed(2));
		}
	}
} else {
	for (let i=0; i<keys.length; i++) {
		let items = table[keys[i]];
		let out = "";
		let casetitle = `${name} (k = ${keys[i]})`;
		const len = name.length + "(k =        )".length;
		let j = 0;
		set.forEach(x => {out += items.has(x)? marks[j>=ml_new?2:0] : marks[1];j++; });
		console.log(fmt.alignLeft(casetitle, len), fmt.alignLeft(`(${items.size}/${set.size}):`, 10), out);
	}
	if (ml_mode) {
		const mlonly = new Set([...mlset].filter(x => !baseset.has(x)));
		const baseonly = new Set([...baseset].filter(x => !mlset.has(x)));
		console.log(`* ML new alarms: ${mlonly.size}`);
		console.log(`* ML missing alarms: ${baseonly.size}`);
	}
	if (Object.keys(reports).length > 0) {
		console.log("* Alarm stats:");
		for (let i in reports) {
			console.log(`  - ${i} : ${Object.keys(reports[i]).length}`);
		}
	}
}
