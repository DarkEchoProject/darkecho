const test=require('node:test');
const assert=require('node:assert/strict');
const {normalize,matches,cleanSaved,parseSaved}=require('../assets/catalog-tools.js');

test('search matches words in any order',()=>assert.ok(matches('She Saw Her Dead Mother in the Mirror','mirror mother')));
test('search requires every word',()=>assert.equal(matches('The Reflection','reflection volcano'),false));
test('search ignores accent marks',()=>assert.ok(matches('Türkiye Earthquake','turkiye')));
test('search ignores apostrophe variants',()=>{
  assert.ok(matches('Don’t Look Under Your Bed',"don't bed"));
  assert.ok(matches('Hawaiʻi','hawaii'));
});
test('search keeps non-Latin words usable',()=>assert.ok(matches('قصة رعب في المرآة','رعب قصة')));
test('punctuation and whitespace alone show all results',()=>assert.ok(matches('Some title',' —  ... ')));
test('normalization handles null safely',()=>assert.equal(normalize(null),''));
test('saved IDs are unique and ordered',()=>assert.deepEqual(cleanSaved(['kGAShG1Pj8s','MuGz3YKRYNk','kGAShG1Pj8s']),['kGAShG1Pj8s','MuGz3YKRYNk']));
test('saved IDs reject objects and unsafe strings',()=>assert.deepEqual(cleanSaved([{},null,'<script>',42,'kGAShG1Pj8s']),['kGAShG1Pj8s']));
test('saved data handles malformed and excessive storage',()=>{
  for(const raw of ['{','null','{}','"kGAShG1Pj8s"',' '.repeat(20001),null])assert.deepEqual(parseSaved(raw),[]);
});
test('saved IDs can be checked against the current catalog',()=>assert.deepEqual(cleanSaved(['kGAShG1Pj8s','MuGz3YKRYNk'],new Set(['MuGz3YKRYNk'])),['MuGz3YKRYNk']));
