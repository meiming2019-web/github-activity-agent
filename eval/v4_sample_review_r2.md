# v4 Round 2 Manual Sample Review

The original 22-question package remains unchanged. All its identities are included below using the current questions; substantive replacements are explicitly marked. Human Round 1 comments have not been supplied, so no signature, finding, or approval is invented.

Selection is explicit window_expression x family stratification: retain the original 22 IDs; for every still-uncovered actual expression, choose a family with the smallest current selected count, breaking ties by family ID and then question ID. No fixed-stride sampling and no difficulty-based selection are used.

Extending one day beyond coverage is answer-neutral for non-calendar aggregates because the extra day has no data. For questions using generate_series date scaffolds, the extra day may add a zero-count row and change the row set; the neutrality conclusion does not apply. Out-of-coverage perturbations are nevertheless excluded uniformly. Detecting these endpoint mistakes is deferred to future analysis-stage SQL window-endpoint parsing, which is not implemented in this phase; row-set grading cannot provide that guarantee.

## Change classification and complete ID inventories

Record-level changes include new sensitivity evidence; they must not be interpreted as entity replacements. Substantive changes are the union of question text, reference SQL, reference columns/rows, and entity parameters.
```json
{
  "old_questions_sha256": "1e33b109a3af2ffcd74926e49876332cd6173bc6a5476000b623fe9689877067",
  "new_questions_sha256": "829ec0475c1ba1c090c8b1926221124df092af8b35b81ccc2a0a92e1fa897dc1",
  "original_review_sha256": "8668908ccfc54b2ee89673a37574e9c6a2f6f00fb409c50661c8dbdffc8c6278",
  "record_changed_ids": [
    "v4_001",
    "v4_002",
    "v4_003",
    "v4_004",
    "v4_005",
    "v4_006",
    "v4_007",
    "v4_008",
    "v4_009",
    "v4_010",
    "v4_011",
    "v4_012",
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_016",
    "v4_017",
    "v4_018",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_028",
    "v4_029",
    "v4_030",
    "v4_031",
    "v4_032",
    "v4_033",
    "v4_034",
    "v4_035",
    "v4_036",
    "v4_037",
    "v4_038",
    "v4_039",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_043",
    "v4_044",
    "v4_045",
    "v4_046",
    "v4_047",
    "v4_048",
    "v4_049",
    "v4_050",
    "v4_051",
    "v4_052",
    "v4_053",
    "v4_054",
    "v4_055",
    "v4_056",
    "v4_057",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_061",
    "v4_062",
    "v4_063",
    "v4_064",
    "v4_065",
    "v4_066",
    "v4_067",
    "v4_068",
    "v4_069",
    "v4_070",
    "v4_071",
    "v4_072",
    "v4_073",
    "v4_074",
    "v4_075",
    "v4_076",
    "v4_077",
    "v4_078",
    "v4_079",
    "v4_080",
    "v4_081",
    "v4_082",
    "v4_083",
    "v4_084",
    "v4_085",
    "v4_086",
    "v4_087",
    "v4_088",
    "v4_089",
    "v4_090",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_094",
    "v4_095",
    "v4_096",
    "v4_097",
    "v4_098",
    "v4_099",
    "v4_100",
    "v4_101",
    "v4_102",
    "v4_103",
    "v4_104",
    "v4_105",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_109",
    "v4_110",
    "v4_111",
    "v4_112",
    "v4_113",
    "v4_114",
    "v4_115",
    "v4_116",
    "v4_117",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_124",
    "v4_125",
    "v4_126",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_142",
    "v4_143",
    "v4_144",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_148",
    "v4_149",
    "v4_150",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_169",
    "v4_170",
    "v4_171",
    "v4_172",
    "v4_173",
    "v4_174",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_178",
    "v4_179",
    "v4_180",
    "v4_181",
    "v4_182",
    "v4_183",
    "v4_184",
    "v4_185",
    "v4_186",
    "v4_187",
    "v4_188",
    "v4_189",
    "v4_190",
    "v4_191",
    "v4_192",
    "v4_193",
    "v4_194",
    "v4_195",
    "v4_196",
    "v4_197",
    "v4_198",
    "v4_199",
    "v4_200",
    "v4_201",
    "v4_202",
    "v4_203",
    "v4_204",
    "v4_205",
    "v4_206",
    "v4_207",
    "v4_208",
    "v4_209",
    "v4_210",
    "v4_211",
    "v4_212",
    "v4_213",
    "v4_214",
    "v4_215",
    "v4_216",
    "v4_217",
    "v4_218",
    "v4_219",
    "v4_220",
    "v4_221",
    "v4_222",
    "v4_223",
    "v4_224",
    "v4_225",
    "v4_226",
    "v4_227",
    "v4_228",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_232",
    "v4_233",
    "v4_234",
    "v4_235",
    "v4_236",
    "v4_237",
    "v4_238",
    "v4_239",
    "v4_240",
    "v4_241",
    "v4_242",
    "v4_243",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_247",
    "v4_248",
    "v4_249",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_253",
    "v4_254",
    "v4_255",
    "v4_256",
    "v4_257",
    "v4_258",
    "v4_259",
    "v4_260",
    "v4_261",
    "v4_262",
    "v4_263",
    "v4_264",
    "v4_265",
    "v4_266",
    "v4_267",
    "v4_268",
    "v4_269",
    "v4_270",
    "v4_271",
    "v4_272",
    "v4_273",
    "v4_274",
    "v4_275",
    "v4_276",
    "v4_277",
    "v4_278",
    "v4_279",
    "v4_280",
    "v4_281",
    "v4_282",
    "v4_283",
    "v4_284",
    "v4_285",
    "v4_286",
    "v4_287",
    "v4_288",
    "v4_289",
    "v4_290",
    "v4_291",
    "v4_292",
    "v4_293",
    "v4_294",
    "v4_295",
    "v4_296",
    "v4_297",
    "v4_298",
    "v4_299",
    "v4_300"
  ],
  "question_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "answer_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "reference_sql_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "parameters_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "substantive_changed_ids": [
    "v4_013",
    "v4_014",
    "v4_015",
    "v4_019",
    "v4_020",
    "v4_021",
    "v4_022",
    "v4_023",
    "v4_024",
    "v4_025",
    "v4_026",
    "v4_027",
    "v4_040",
    "v4_041",
    "v4_042",
    "v4_058",
    "v4_059",
    "v4_060",
    "v4_091",
    "v4_092",
    "v4_093",
    "v4_106",
    "v4_107",
    "v4_108",
    "v4_118",
    "v4_119",
    "v4_120",
    "v4_121",
    "v4_122",
    "v4_123",
    "v4_127",
    "v4_128",
    "v4_129",
    "v4_130",
    "v4_131",
    "v4_132",
    "v4_133",
    "v4_134",
    "v4_135",
    "v4_136",
    "v4_137",
    "v4_138",
    "v4_139",
    "v4_140",
    "v4_141",
    "v4_145",
    "v4_146",
    "v4_147",
    "v4_151",
    "v4_152",
    "v4_153",
    "v4_154",
    "v4_155",
    "v4_156",
    "v4_157",
    "v4_158",
    "v4_159",
    "v4_160",
    "v4_161",
    "v4_162",
    "v4_163",
    "v4_164",
    "v4_165",
    "v4_166",
    "v4_167",
    "v4_168",
    "v4_175",
    "v4_176",
    "v4_177",
    "v4_229",
    "v4_230",
    "v4_231",
    "v4_244",
    "v4_245",
    "v4_246",
    "v4_250",
    "v4_251",
    "v4_252",
    "v4_259",
    "v4_260",
    "v4_261"
  ],
  "metadata_only_changed_ids": [
    "v4_001",
    "v4_002",
    "v4_003",
    "v4_004",
    "v4_005",
    "v4_006",
    "v4_007",
    "v4_008",
    "v4_009",
    "v4_010",
    "v4_011",
    "v4_012",
    "v4_016",
    "v4_017",
    "v4_018",
    "v4_028",
    "v4_029",
    "v4_030",
    "v4_031",
    "v4_032",
    "v4_033",
    "v4_034",
    "v4_035",
    "v4_036",
    "v4_037",
    "v4_038",
    "v4_039",
    "v4_043",
    "v4_044",
    "v4_045",
    "v4_046",
    "v4_047",
    "v4_048",
    "v4_049",
    "v4_050",
    "v4_051",
    "v4_052",
    "v4_053",
    "v4_054",
    "v4_055",
    "v4_056",
    "v4_057",
    "v4_061",
    "v4_062",
    "v4_063",
    "v4_064",
    "v4_065",
    "v4_066",
    "v4_067",
    "v4_068",
    "v4_069",
    "v4_070",
    "v4_071",
    "v4_072",
    "v4_073",
    "v4_074",
    "v4_075",
    "v4_076",
    "v4_077",
    "v4_078",
    "v4_079",
    "v4_080",
    "v4_081",
    "v4_082",
    "v4_083",
    "v4_084",
    "v4_085",
    "v4_086",
    "v4_087",
    "v4_088",
    "v4_089",
    "v4_090",
    "v4_094",
    "v4_095",
    "v4_096",
    "v4_097",
    "v4_098",
    "v4_099",
    "v4_100",
    "v4_101",
    "v4_102",
    "v4_103",
    "v4_104",
    "v4_105",
    "v4_109",
    "v4_110",
    "v4_111",
    "v4_112",
    "v4_113",
    "v4_114",
    "v4_115",
    "v4_116",
    "v4_117",
    "v4_124",
    "v4_125",
    "v4_126",
    "v4_142",
    "v4_143",
    "v4_144",
    "v4_148",
    "v4_149",
    "v4_150",
    "v4_169",
    "v4_170",
    "v4_171",
    "v4_172",
    "v4_173",
    "v4_174",
    "v4_178",
    "v4_179",
    "v4_180",
    "v4_181",
    "v4_182",
    "v4_183",
    "v4_184",
    "v4_185",
    "v4_186",
    "v4_187",
    "v4_188",
    "v4_189",
    "v4_190",
    "v4_191",
    "v4_192",
    "v4_193",
    "v4_194",
    "v4_195",
    "v4_196",
    "v4_197",
    "v4_198",
    "v4_199",
    "v4_200",
    "v4_201",
    "v4_202",
    "v4_203",
    "v4_204",
    "v4_205",
    "v4_206",
    "v4_207",
    "v4_208",
    "v4_209",
    "v4_210",
    "v4_211",
    "v4_212",
    "v4_213",
    "v4_214",
    "v4_215",
    "v4_216",
    "v4_217",
    "v4_218",
    "v4_219",
    "v4_220",
    "v4_221",
    "v4_222",
    "v4_223",
    "v4_224",
    "v4_225",
    "v4_226",
    "v4_227",
    "v4_228",
    "v4_232",
    "v4_233",
    "v4_234",
    "v4_235",
    "v4_236",
    "v4_237",
    "v4_238",
    "v4_239",
    "v4_240",
    "v4_241",
    "v4_242",
    "v4_243",
    "v4_247",
    "v4_248",
    "v4_249",
    "v4_253",
    "v4_254",
    "v4_255",
    "v4_256",
    "v4_257",
    "v4_258",
    "v4_262",
    "v4_263",
    "v4_264",
    "v4_265",
    "v4_266",
    "v4_267",
    "v4_268",
    "v4_269",
    "v4_270",
    "v4_271",
    "v4_272",
    "v4_273",
    "v4_274",
    "v4_275",
    "v4_276",
    "v4_277",
    "v4_278",
    "v4_279",
    "v4_280",
    "v4_281",
    "v4_282",
    "v4_283",
    "v4_284",
    "v4_285",
    "v4_286",
    "v4_287",
    "v4_288",
    "v4_289",
    "v4_290",
    "v4_291",
    "v4_292",
    "v4_293",
    "v4_294",
    "v4_295",
    "v4_296",
    "v4_297",
    "v4_298",
    "v4_299",
    "v4_300"
  ],
  "original_review_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_121",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_231",
    "v4_241",
    "v4_246",
    "v4_256",
    "v4_261",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291"
  ],
  "reviewed_replacement_ids": [
    "v4_121",
    "v4_231",
    "v4_246",
    "v4_261"
  ],
  "reviewed_metadata_only_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_241",
    "v4_256",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291"
  ],
  "selected_ids": [
    "v4_001",
    "v4_006",
    "v4_061",
    "v4_066",
    "v4_121",
    "v4_126",
    "v4_181",
    "v4_186",
    "v4_196",
    "v4_201",
    "v4_211",
    "v4_216",
    "v4_226",
    "v4_231",
    "v4_241",
    "v4_246",
    "v4_256",
    "v4_261",
    "v4_271",
    "v4_276",
    "v4_286",
    "v4_291",
    "v4_127",
    "v4_079",
    "v4_262",
    "v4_031",
    "v4_160",
    "v4_190",
    "v4_238",
    "v4_115",
    "v4_139",
    "v4_157",
    "v4_175"
  ],
  "window_expressions": [
    "the last 7 days",
    "last week",
    "previous week",
    "October 8 through October 9, 2026",
    "October 8 through October 10, 2026",
    "October 8 through October 12, 2026",
    "October 8 through October 14, 2026",
    "October 8 through October 17, 2026",
    "October 8 through October 21, 2026",
    "October 15 through October 21, 2026",
    "October 11 through October 12, 2026",
    "October 10 through October 16, 2026",
    "October 11 through October 17, 2026"
  ]
}
```

## Selected window/family strata

| ID | Window expression | Family | Selection reason |
| --- | --- | --- | --- |
| v4_001 | the last 7 days | window_new_stars | original_22_identity |
| v4_006 | the last 7 days | window_new_stars | original_22_identity |
| v4_061 | the last 7 days | window_collaboration_events | original_22_identity |
| v4_066 | the last 7 days | window_collaboration_events | original_22_identity |
| v4_121 | the last 7 days | window_active_contributors | original_22_identity, replacement_of_reviewed_question |
| v4_126 | the last 7 days | window_active_contributors | original_22_identity |
| v4_181 | the last 7 days | daily_trend | original_22_identity |
| v4_186 | previous week | daily_trend | original_22_identity |
| v4_196 | the last 7 days | running_total | original_22_identity |
| v4_201 | previous week | running_total | original_22_identity |
| v4_211 | the last 7 days | day_over_day | original_22_identity |
| v4_216 | previous week | day_over_day | original_22_identity |
| v4_226 | the last 7 days | day_of_week | original_22_identity |
| v4_231 | previous week | day_of_week | original_22_identity, replacement_of_reviewed_question |
| v4_241 | the last 7 days | session_segmentation | original_22_identity |
| v4_246 | previous week | session_segmentation | original_22_identity, replacement_of_reviewed_question |
| v4_256 | the last 7 days | consecutive_day_runs | original_22_identity |
| v4_261 | previous week | consecutive_day_runs | original_22_identity, replacement_of_reviewed_question |
| v4_271 | None | catalog_lookup | original_22_identity |
| v4_276 | None | catalog_lookup | original_22_identity |
| v4_286 | None | language_composition | original_22_identity |
| v4_291 | None | language_composition | original_22_identity |
| v4_127 | last week | window_active_contributors | uncovered_window_expression, stratum=last week x window_active_contributors |
| v4_079 | October 8 through October 9, 2026 | window_collaboration_events | uncovered_window_expression, stratum=October 8 through October 9, 2026 x window_collaboration_events |
| v4_262 | October 8 through October 10, 2026 | consecutive_day_runs | uncovered_window_expression, stratum=October 8 through October 10, 2026 x consecutive_day_runs |
| v4_031 | October 8 through October 12, 2026 | window_new_stars | uncovered_window_expression, stratum=October 8 through October 12, 2026 x window_new_stars |
| v4_160 | October 8 through October 14, 2026 | window_active_contributors | uncovered_window_expression, stratum=October 8 through October 14, 2026 x window_active_contributors |
| v4_190 | October 8 through October 17, 2026 | daily_trend | uncovered_window_expression, stratum=October 8 through October 17, 2026 x daily_trend |
| v4_238 | October 8 through October 21, 2026 | day_of_week | uncovered_window_expression, stratum=October 8 through October 21, 2026 x day_of_week |
| v4_115 | October 15 through October 21, 2026 | window_collaboration_events | uncovered_window_expression, stratum=October 15 through October 21, 2026 x window_collaboration_events |
| v4_139 | October 11 through October 12, 2026 | window_active_contributors | uncovered_window_expression, stratum=October 11 through October 12, 2026 x window_active_contributors |
| v4_157 | October 10 through October 16, 2026 | window_active_contributors | uncovered_window_expression, stratum=October 10 through October 16, 2026 x window_active_contributors |
| v4_175 | October 11 through October 17, 2026 | window_active_contributors | uncovered_window_expression, stratum=October 11 through October 17, 2026 x window_active_contributors |

## v4_001 — window_new_stars / literal

Selection: original_22_identity.

For the last 7 days, report new_stars for repository 'firecrawl/firecrawl' as value. Count distinct non-null WatchEvent actors, including bots; apply the definition separately per repository within the window.

```sql
SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows": [
      [
        29
      ]
    ],
    "rows_sha256": "51cc38ae7f7ec48474a2911c196358ba237244d842eee4f6032d6ad53816d731",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows": [
      [
        35
      ]
    ],
    "rows_sha256": "82712f790a1d18c6fe08d88403992901d6d8833369ef6440019becb434944c2c",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows": [
      [
        46
      ]
    ],
    "rows_sha256": "af6b5b14ba7e9aa527f77830e5899e35be955fd36b909ee58bdcbeb2eb164140",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'firecrawl/firecrawl'",
    "row_count": 1,
    "rows": [
      [
        42
      ]
    ],
    "rows_sha256": "521488a321ba20132908087a5cfa920bd098afadef61d84ea0de2f7e8783f021",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_006 — window_new_stars / distractor

Selection: original_22_identity.

For the last 7 days, rank up to five 'Shell' repositories with positive new_stars; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count distinct non-null WatchEvent actors, including bots; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 4.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows": [
      [
        "mattpocock/skills",
        122
      ],
      [
        "obra/superpowers",
        66
      ],
      [
        "msitarzewski/agency-agents",
        51
      ],
      [
        "ohmyzsh/ohmyzsh",
        2
      ]
    ],
    "rows_sha256": "e8917ede30cf66cda74dddc8ad945e7e382403b020806e47725faf0acee62ace",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows": [
      [
        "mattpocock/skills",
        134
      ],
      [
        "obra/superpowers",
        72
      ],
      [
        "msitarzewski/agency-agents",
        42
      ],
      [
        "ohmyzsh/ohmyzsh",
        2
      ]
    ],
    "rows_sha256": "cd5db3dbcd6d67626a5b3f8e6aa0d17e4e8441275ca2f8096c68993f999d473d",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows": [
      [
        "mattpocock/skills",
        179
      ],
      [
        "obra/superpowers",
        91
      ],
      [
        "msitarzewski/agency-agents",
        58
      ],
      [
        "ohmyzsh/ohmyzsh",
        2
      ]
    ],
    "rows_sha256": "ca5a2d677bad4c6757b41dbc0cd3f4bec6948217def0de803546e396285e1352",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Shell' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows": [
      [
        "mattpocock/skills",
        165
      ],
      [
        "obra/superpowers",
        85
      ],
      [
        "msitarzewski/agency-agents",
        48
      ],
      [
        "ohmyzsh/ohmyzsh",
        2
      ]
    ],
    "rows_sha256": "ff8800a4e2ed7ed4d73a71c05c0d89bb8c4bb570948ae19b0712573344664b5e",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_061 — window_collaboration_events / literal

Selection: original_22_identity.

For the last 7 days, report collaboration_events for repository 'morluto/rea' as value. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window.

```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows": [
      [
        131
      ]
    ],
    "rows_sha256": "50f2233e4a2a3194806c957007177802d49be1f4c6df0d2b7751ed635025d6e3",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows": [
      [
        152
      ]
    ],
    "rows_sha256": "1f17f598759845f7b8d8bae13917d8ac98bca3f70a76526ab4093849d6ddca80",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows": [
      [
        224
      ]
    ],
    "rows_sha256": "684a69a7192436c60923e5e2a19402ccd14905d19fbbfa4cb233774cc8081974",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'morluto/rea'",
    "row_count": 1,
    "rows": [
      [
        206
      ]
    ],
    "rows_sha256": "2fa2c8b080d5e916c4e0c20371f1e90d2014afaea0c54e64e7fb6974c4a056db",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_066 — window_collaboration_events / distractor

Selection: original_22_identity.

For the last 7 days, rank up to five 'Python' repositories with positive collaboration_events; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 5.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows": [
      [
        "NousResearch/hermes-agent",
        565
      ],
      [
        "Significant-Gravitas/AutoGPT",
        88
      ],
      [
        "langgenius/dify",
        39
      ],
      [
        "huggingface/transformers",
        37
      ],
      [
        "langflow-ai/langflow",
        18
      ]
    ],
    "rows_sha256": "d62db7c4f8c41f5d9afcf05471e7ab7964c822d35265f2daf28f6ec2e685f5f1",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows": [
      [
        "NousResearch/hermes-agent",
        619
      ],
      [
        "Significant-Gravitas/AutoGPT",
        89
      ],
      [
        "langgenius/dify",
        38
      ],
      [
        "huggingface/transformers",
        32
      ],
      [
        "langflow-ai/langflow",
        23
      ]
    ],
    "rows_sha256": "d22ba0ef1cddb095b49af5cd1570267ed02a6d003b1e2351dda156d1b7a1e167",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows": [
      [
        "NousResearch/hermes-agent",
        721
      ],
      [
        "Significant-Gravitas/AutoGPT",
        109
      ],
      [
        "langgenius/dify",
        56
      ],
      [
        "huggingface/transformers",
        46
      ],
      [
        "langflow-ai/langflow",
        32
      ]
    ],
    "rows_sha256": "3e1d1596261c537ad85e5dfa53ed2a33c48b1c05691d252f612719cdb5825bca",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH metric AS (SELECT e.repo_name, COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Python' GROUP BY e.repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows": [
      [
        "NousResearch/hermes-agent",
        678
      ],
      [
        "Significant-Gravitas/AutoGPT",
        94
      ],
      [
        "langgenius/dify",
        49
      ],
      [
        "huggingface/transformers",
        38
      ],
      [
        "langflow-ai/langflow",
        30
      ]
    ],
    "rows_sha256": "a9632a0e3460a6108f07f52f6175893c6875e018c3467a12a6b95f2c40168096",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_121 — window_active_contributors / literal

Selection: original_22_identity, replacement_of_reviewed_question.

For the last 7 days, report active_contributors for repository 'NousResearch/hermes-agent' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'NousResearch/hermes-agent' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

**REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID — requires renewed human review.**

Previous question:
For the last 7 days, report active_contributors for repository 'morluto/rea' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

Previous reference rows:
```json
[
  [
    8
  ]
]
```

Current reference rows:
```json
[
  [
    14
  ]
]
```

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'NousResearch/hermes-agent' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        12
      ]
    ],
    "rows_sha256": "bd9f136b622b85cf21ee24ea2aad17d5131a056dbc482a5c3d3a26e54753d667",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'NousResearch/hermes-agent' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'NousResearch/hermes-agent' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        15
      ]
    ],
    "rows_sha256": "bc54a496c58cd6946984014c34865e5dcc1443494b29dce0c089e80f4690c9c7",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'NousResearch/hermes-agent' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_126 — window_active_contributors / distractor

Selection: original_22_identity.

For the last 7 days, rank up to five 'Rust' repositories with positive active_contributors; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['repo_name', 'value']`; reference row count: 4.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 4,
    "rows": [
      [
        "rust-lang/rust",
        5
      ],
      [
        "farion1231/cc-switch",
        2
      ],
      [
        "clash-verge-rev/clash-verge-rev",
        1
      ],
      [
        "openai/codex",
        1
      ]
    ],
    "rows_sha256": "32ca90f340f7a11cee4e20ebf257f6084ad1651f4726e3381ec9f654a7be0852",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 3,
    "rows": [
      [
        "rust-lang/rust",
        6
      ],
      [
        "farion1231/cc-switch",
        2
      ],
      [
        "openai/codex",
        1
      ]
    ],
    "rows_sha256": "f1c1bec8669168cc3b875426672876e873e0b740e72e6cfdd377eeaf7e2a7fcf",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 5,
    "rows": [
      [
        "rust-lang/rust",
        6
      ],
      [
        "farion1231/cc-switch",
        3
      ],
      [
        "clash-verge-rev/clash-verge-rev",
        1
      ],
      [
        "openai/codex",
        1
      ],
      [
        "rustdesk/rustdesk",
        1
      ]
    ],
    "rows_sha256": "c865c182cfd61c707de6370af038898d2c23c40e17b266e3914d8cd0fa692b61",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND r.language = 'Rust' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 3,
    "rows": [
      [
        "rust-lang/rust",
        6
      ],
      [
        "farion1231/cc-switch",
        2
      ],
      [
        "openai/codex",
        1
      ]
    ],
    "rows_sha256": "f1c1bec8669168cc3b875426672876e873e0b740e72e6cfdd377eeaf7e2a7fcf",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-15, 2026-10-22)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_181 — daily_trend / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'Hack-with-Github/Awesome-Hacking', return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-16",
        4
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        1
      ],
      [
        "2026-10-19",
        1
      ],
      [
        "2026-10-20",
        2
      ],
      [
        "2026-10-21",
        0
      ]
    ],
    "rows_sha256": "866f5b5e188f6033ed4fe8fd2e2a583757c1e4c15450891aa44fcde4a2d6c787",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-15",
        1
      ],
      [
        "2026-10-16",
        4
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        1
      ],
      [
        "2026-10-19",
        1
      ],
      [
        "2026-10-20",
        2
      ]
    ],
    "rows_sha256": "dee7005228a6907d28f4fc4853f39916a8fe672e64c5cdac06545f069331877b",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        1
      ],
      [
        "2026-10-16",
        4
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        1
      ],
      [
        "2026-10-19",
        1
      ],
      [
        "2026-10-20",
        2
      ],
      [
        "2026-10-21",
        0
      ]
    ],
    "rows_sha256": "727b0862d86b4bcf16e1b61e3847f94cad035c452ecafd0d5ec9f6ef8bde3361",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'Hack-with-Github/Awesome-Hacking' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        1
      ],
      [
        "2026-10-16",
        4
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        1
      ],
      [
        "2026-10-19",
        1
      ],
      [
        "2026-10-20",
        2
      ]
    ],
    "rows_sha256": "693c2a3f0ef5a4625d38c1d00c663e1adeda773405ad275c6fb5bbf42f6a0dd6",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_186 — daily_trend / distractor

Selection: original_22_identity.

For previous week, using PushEvent records for 'mattpocock/skills', return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-09",
        0
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        0
      ],
      [
        "2026-10-12",
        0
      ],
      [
        "2026-10-13",
        0
      ],
      [
        "2026-10-14",
        0
      ]
    ],
    "rows_sha256": "4ef11052a808269886193421ba294cde4708c34efa2936022d511ecf4064c180",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-08",
        1
      ],
      [
        "2026-10-09",
        0
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        0
      ],
      [
        "2026-10-12",
        0
      ],
      [
        "2026-10-13",
        0
      ]
    ],
    "rows_sha256": "e677024fce2cdf7371e730927ac7cc2b971ece42c0650a0324463699c5212ed2",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-08",
        1
      ],
      [
        "2026-10-09",
        0
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        0
      ],
      [
        "2026-10-12",
        0
      ],
      [
        "2026-10-13",
        0
      ],
      [
        "2026-10-14",
        0
      ],
      [
        "2026-10-15",
        0
      ]
    ],
    "rows_sha256": "94c8cdf1d2830b3b8b3ed386834acf44518271ae09c5164bea7b7a77fcabf3f4",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'mattpocock/skills' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-09",
        0
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        0
      ],
      [
        "2026-10-12",
        0
      ],
      [
        "2026-10-13",
        0
      ],
      [
        "2026-10-14",
        0
      ],
      [
        "2026-10-15",
        0
      ]
    ],
    "rows_sha256": "35f2b66ec891b80b235bb89827739e7b0f1dd5580f257c6d398db634ab8331b2",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_196 — running_total / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'ollama/ollama', return each UTC date as day, event_count, and running_count accumulated from the window start, including zero-count dates, ordered by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count', 'running_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-16",
        2,
        2
      ],
      [
        "2026-10-17",
        0,
        2
      ],
      [
        "2026-10-18",
        5,
        7
      ],
      [
        "2026-10-19",
        0,
        7
      ],
      [
        "2026-10-20",
        4,
        11
      ],
      [
        "2026-10-21",
        2,
        13
      ]
    ],
    "rows_sha256": "b11bf5207cd0b26c363975dd7a4b7a8b81ca8dbc927c87eebdef34ff6a2fab8f",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-15",
        2,
        2
      ],
      [
        "2026-10-16",
        2,
        4
      ],
      [
        "2026-10-17",
        0,
        4
      ],
      [
        "2026-10-18",
        5,
        9
      ],
      [
        "2026-10-19",
        0,
        9
      ],
      [
        "2026-10-20",
        4,
        13
      ]
    ],
    "rows_sha256": "ac965c99eec2b4660da6c82c2f20c2eef4164dbe84d2472f4facb3604f6e9dc8",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-14",
        0,
        0
      ],
      [
        "2026-10-15",
        2,
        2
      ],
      [
        "2026-10-16",
        2,
        4
      ],
      [
        "2026-10-17",
        0,
        4
      ],
      [
        "2026-10-18",
        5,
        9
      ],
      [
        "2026-10-19",
        0,
        9
      ],
      [
        "2026-10-20",
        4,
        13
      ],
      [
        "2026-10-21",
        2,
        15
      ]
    ],
    "rows_sha256": "38b32025d26162aee1504079d66820a53e5448b696fe3546a59b3a5f0cc07985",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'ollama/ollama' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-14",
        0,
        0
      ],
      [
        "2026-10-15",
        2,
        2
      ],
      [
        "2026-10-16",
        2,
        4
      ],
      [
        "2026-10-17",
        0,
        4
      ],
      [
        "2026-10-18",
        5,
        9
      ],
      [
        "2026-10-19",
        0,
        9
      ],
      [
        "2026-10-20",
        4,
        13
      ]
    ],
    "rows_sha256": "24063135447c7f29673ce649b53f33e7d36d7c1cf5af2596a0bf1df42a1c18ac",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_201 — running_total / distractor

Selection: original_22_identity.

For previous week, using PushEvent records for 'ollama/ollama', return each UTC date as day, event_count, and running_count accumulated from the window start, including zero-count dates, ordered by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count', 'running_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-09",
        0,
        0
      ],
      [
        "2026-10-10",
        0,
        0
      ],
      [
        "2026-10-11",
        0,
        0
      ],
      [
        "2026-10-12",
        4,
        4
      ],
      [
        "2026-10-13",
        7,
        11
      ],
      [
        "2026-10-14",
        0,
        11
      ]
    ],
    "rows_sha256": "fdd664220176ecd412f5c061f638de8f33256e9f1460bc1ca204d79fb7cc9799",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-08",
        1,
        1
      ],
      [
        "2026-10-09",
        0,
        1
      ],
      [
        "2026-10-10",
        0,
        1
      ],
      [
        "2026-10-11",
        0,
        1
      ],
      [
        "2026-10-12",
        4,
        5
      ],
      [
        "2026-10-13",
        7,
        12
      ]
    ],
    "rows_sha256": "c27b022347818c752794d4386cd2ddbcb3f7febca9291d3e1102e80f0a170808",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-08",
        1,
        1
      ],
      [
        "2026-10-09",
        0,
        1
      ],
      [
        "2026-10-10",
        0,
        1
      ],
      [
        "2026-10-11",
        0,
        1
      ],
      [
        "2026-10-12",
        4,
        5
      ],
      [
        "2026-10-13",
        7,
        12
      ],
      [
        "2026-10-14",
        0,
        12
      ],
      [
        "2026-10-15",
        0,
        12
      ]
    ],
    "rows_sha256": "afe56f4b3c281b1ca8142a9e0acdb793ec5a601dd353d8e8f44bd76d95c2010e",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'ollama/ollama' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count, SUM(event_count) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count FROM daily ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-09",
        0,
        0
      ],
      [
        "2026-10-10",
        0,
        0
      ],
      [
        "2026-10-11",
        0,
        0
      ],
      [
        "2026-10-12",
        4,
        4
      ],
      [
        "2026-10-13",
        7,
        11
      ],
      [
        "2026-10-14",
        0,
        11
      ],
      [
        "2026-10-15",
        0,
        11
      ]
    ],
    "rows_sha256": "12ab226d74853ef34934559f8decb649f3c34799fee34b681cc84539b686148d",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_211 — day_over_day / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'AUTOMATIC1111/stable-diffusion-webui', return each UTC date as day, event_count, previous_count, and change (current minus previous); include zero-count dates and use NULL for previous_count and change on the first date; order by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['day', 'event_count', 'previous_count', 'change']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-16",
        1,
        null,
        null
      ],
      [
        "2026-10-17",
        0,
        1,
        -1
      ],
      [
        "2026-10-18",
        0,
        0,
        0
      ],
      [
        "2026-10-19",
        1,
        0,
        1
      ],
      [
        "2026-10-20",
        1,
        1,
        0
      ],
      [
        "2026-10-21",
        0,
        1,
        -1
      ]
    ],
    "rows_sha256": "54241e83c40f27cd467ff3794cacdc1804aa359665086e7a0bc4172052644065",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-15",
        0,
        null,
        null
      ],
      [
        "2026-10-16",
        1,
        0,
        1
      ],
      [
        "2026-10-17",
        0,
        1,
        -1
      ],
      [
        "2026-10-18",
        0,
        0,
        0
      ],
      [
        "2026-10-19",
        1,
        0,
        1
      ],
      [
        "2026-10-20",
        1,
        1,
        0
      ]
    ],
    "rows_sha256": "8c6823ea66a9b4a1842e5e9421f0f4ce3032c444f7885a6d20205d8882007230",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-14",
        2,
        null,
        null
      ],
      [
        "2026-10-15",
        0,
        2,
        -2
      ],
      [
        "2026-10-16",
        1,
        0,
        1
      ],
      [
        "2026-10-17",
        0,
        1,
        -1
      ],
      [
        "2026-10-18",
        0,
        0,
        0
      ],
      [
        "2026-10-19",
        1,
        0,
        1
      ],
      [
        "2026-10-20",
        1,
        1,
        0
      ],
      [
        "2026-10-21",
        0,
        1,
        -1
      ]
    ],
    "rows_sha256": "61839d525250022a0f6ec7f72c1d04f13e6ee37afa554d27028ad313e5b4ad7e",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'AUTOMATIC1111/stable-diffusion-webui' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-14",
        2,
        null,
        null
      ],
      [
        "2026-10-15",
        0,
        2,
        -2
      ],
      [
        "2026-10-16",
        1,
        0,
        1
      ],
      [
        "2026-10-17",
        0,
        1,
        -1
      ],
      [
        "2026-10-18",
        0,
        0,
        0
      ],
      [
        "2026-10-19",
        1,
        0,
        1
      ],
      [
        "2026-10-20",
        1,
        1,
        0
      ]
    ],
    "rows_sha256": "967d503a6dbebf91129069aa6d0e2af07b85fac68911b055cd2ffd9695ea5c7f",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_216 — day_over_day / distractor

Selection: original_22_identity.

For previous week, using PushEvent records for 'langgenius/dify', return each UTC date as day, event_count, previous_count, and change (current minus previous); include zero-count dates and use NULL for previous_count and change on the first date; order by day ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['day', 'event_count', 'previous_count', 'change']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-09",
        15,
        null,
        null
      ],
      [
        "2026-10-10",
        15,
        15,
        0
      ],
      [
        "2026-10-11",
        4,
        15,
        -11
      ],
      [
        "2026-10-12",
        19,
        4,
        15
      ],
      [
        "2026-10-13",
        31,
        19,
        12
      ],
      [
        "2026-10-14",
        15,
        31,
        -16
      ]
    ],
    "rows_sha256": "cada6cb3631a7ba12a6766a5e06314f1560fbbbc37814636926c57da7e81b1cd",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 6,
    "rows": [
      [
        "2026-10-08",
        12,
        null,
        null
      ],
      [
        "2026-10-09",
        15,
        12,
        3
      ],
      [
        "2026-10-10",
        15,
        15,
        0
      ],
      [
        "2026-10-11",
        4,
        15,
        -11
      ],
      [
        "2026-10-12",
        19,
        4,
        15
      ],
      [
        "2026-10-13",
        31,
        19,
        12
      ]
    ],
    "rows_sha256": "c34f4d8ea3f3701132422e9991a7793287c5cf7ae2e269cda8890c45e922dd95",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 8,
    "rows": [
      [
        "2026-10-08",
        12,
        null,
        null
      ],
      [
        "2026-10-09",
        15,
        12,
        3
      ],
      [
        "2026-10-10",
        15,
        15,
        0
      ],
      [
        "2026-10-11",
        4,
        15,
        -11
      ],
      [
        "2026-10-12",
        19,
        4,
        15
      ],
      [
        "2026-10-13",
        31,
        19,
        12
      ],
      [
        "2026-10-14",
        15,
        31,
        -16
      ],
      [
        "2026-10-15",
        0,
        15,
        -15
      ]
    ],
    "rows_sha256": "0ac226847777af832ecf0eba917b5304254268a299e21d641216d9cc0b9ec50a",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'langgenius/dify' AND e.type = 'PushEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) , compared AS (SELECT day, event_count, LAG(event_count) OVER (ORDER BY day) AS previous_count FROM daily) SELECT day, event_count, previous_count, event_count - previous_count AS change FROM compared ORDER BY day ASC",
    "row_count": 7,
    "rows": [
      [
        "2026-10-09",
        15,
        null,
        null
      ],
      [
        "2026-10-10",
        15,
        15,
        0
      ],
      [
        "2026-10-11",
        4,
        15,
        -11
      ],
      [
        "2026-10-12",
        19,
        4,
        15
      ],
      [
        "2026-10-13",
        31,
        19,
        12
      ],
      [
        "2026-10-14",
        15,
        31,
        -16
      ],
      [
        "2026-10-15",
        0,
        15,
        -15
      ]
    ],
    "rows_sha256": "67c19dec3d5635d24aded5a5329a98958eca523968a2bff9651df482f5e910ec",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_226 — day_of_week / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'yangshun/tech-interview-handbook', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['weekday', 'event_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-16', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 6,
    "rows": [
      [
        0,
        0
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        0
      ],
      [
        5,
        1
      ],
      [
        6,
        0
      ]
    ],
    "rows_sha256": "f08e126f80bc969abeb7ea4a2906da79c0e570c62b19b7e072fae5151c9e76d4",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-15', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 6,
    "rows": [
      [
        0,
        0
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        4,
        1
      ],
      [
        5,
        1
      ],
      [
        6,
        0
      ]
    ],
    "rows_sha256": "6439fad9b3b535fb55a56258979699a66d2942274b547d12f7a42902941df4c9",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        0
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        1
      ],
      [
        4,
        1
      ],
      [
        5,
        1
      ],
      [
        6,
        0
      ]
    ],
    "rows_sha256": "9771c015150cb198ad1aec35ec2ed8643332784deee5a3586c0b2e9545d60753",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-14', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'yangshun/tech-interview-handbook' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        0
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        1
      ],
      [
        4,
        1
      ],
      [
        5,
        1
      ],
      [
        6,
        0
      ]
    ],
    "rows_sha256": "9771c015150cb198ad1aec35ec2ed8643332784deee5a3586c0b2e9545d60753",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_231 — day_of_week / distractor

Selection: original_22_identity, replacement_of_reviewed_question.

For previous week, using WatchEvent records for 'Comfy-Org/ComfyUI', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['weekday', 'event_count']`; reference row count: 7.

**REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID — requires renewed human review.**

Previous question:
For previous week, using PushEvent records for 'Comfy-Org/ComfyUI', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending. A repository creation year of 2017 is background only and must not filter the answer.

Previous reference rows:
```json
[
  [
    0,
    2
  ],
  [
    1,
    3
  ],
  [
    2,
    5
  ],
  [
    3,
    2
  ],
  [
    4,
    1
  ],
  [
    5,
    0
  ],
  [
    6,
    6
  ]
]
```

Current reference rows:
```json
[
  [
    0,
    1
  ],
  [
    1,
    2
  ],
  [
    2,
    0
  ],
  [
    3,
    4
  ],
  [
    4,
    5
  ],
  [
    5,
    1
  ],
  [
    6,
    2
  ]
]
```

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-14', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 6,
    "rows": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        3,
        4
      ],
      [
        5,
        1
      ],
      [
        6,
        2
      ]
    ],
    "rows_sha256": "c49366ceebcbdd02ff7c2d4f9f99bb786627f3454dcdb1a45384f1d0eb9019f4",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-13', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 6,
    "rows": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        4,
        5
      ],
      [
        5,
        1
      ],
      [
        6,
        2
      ]
    ],
    "rows_sha256": "8f1c55bb8e9f21f3323b8c805a8173fa0c990b3effbc834005fe545f56244c93",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        3,
        4
      ],
      [
        4,
        6
      ],
      [
        5,
        1
      ],
      [
        6,
        2
      ]
    ],
    "rows_sha256": "d98d3a1ad105995f8ed614b632c467f1c8ac9a2fd2c0f1d5cbf87773355cd808",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-15', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'Comfy-Org/ComfyUI' AND e.type = 'WatchEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        3,
        4
      ],
      [
        4,
        1
      ],
      [
        5,
        1
      ],
      [
        6,
        2
      ]
    ],
    "rows_sha256": "502f551bc2fda1d593de666c47fc8c8398b1163793e3a79c0573d28536edcd89",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_241 — session_segmentation / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'trimstray/the-book-of-secret-knowledge', return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session.

```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['session_count']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        28
      ]
    ],
    "rows_sha256": "5bd2881bfa6bb6e4feb436faf966e3a18c1155a0b2d479a60cdb80a8233f833d",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        28
      ]
    ],
    "rows_sha256": "5bd2881bfa6bb6e4feb436faf966e3a18c1155a0b2d479a60cdb80a8233f833d",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        35
      ]
    ],
    "rows_sha256": "82712f790a1d18c6fe08d88403992901d6d8833369ef6440019becb434944c2c",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'trimstray/the-book-of-secret-knowledge' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        30
      ]
    ],
    "rows_sha256": "1220e80a7a8fb1bcece94f15115f1d7a81ee034c624c43a2168434f6b4265cef",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_246 — session_segmentation / distractor

Selection: original_22_identity, replacement_of_reviewed_question.

For previous week, using WatchEvent records for 'obra/superpowers', return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'obra/superpowers' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['session_count']`; reference row count: 1.

**REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID — requires renewed human review.**

Previous question:
For previous week, using PushEvent records for 'rustdesk/rustdesk', return session_count after ordering these records by created_at and event_id ascending; the first record starts a session, and a gap strictly greater than 30 minutes starts another session. A repository creation year of 2017 is background only and must not filter the answer.

Previous reference rows:
```json
[
  [
    6
  ]
]
```

Current reference rows:
```json
[
  [
    48
  ]
]
```

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'obra/superpowers' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        45
      ]
    ],
    "rows_sha256": "09596e9cc9963584015b5e9fffa201ec68df99615774734d6f243efa10e89da4",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'obra/superpowers' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        37
      ]
    ],
    "rows_sha256": "be60992747486109d4dc16d216a53438c3d6bf92df5440b55c662d9a2c69ee87",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'obra/superpowers' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        59
      ]
    ],
    "rows_sha256": "1be445d3a466ded3cb6dc05cfbd2e56c856cef9c628350e3b5473eeafbeb85b2",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH ordered AS (SELECT e.created_at, LAG(e.created_at) OVER (ORDER BY e.created_at, e.event_id) AS previous_at FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'obra/superpowers' AND e.type = 'WatchEvent') SELECT SUM(CASE WHEN previous_at IS NULL OR created_at - previous_at > INTERVAL '30 minutes' THEN 1 ELSE 0 END) AS session_count FROM ordered",
    "row_count": 1,
    "rows": [
      [
        56
      ]
    ],
    "rows_sha256": "2b508a00a17e7b0bf2e770ee643f293e325dc19678f73a01e1929917220849af",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_256 — consecutive_day_runs / literal

Selection: original_22_identity.

For the last 7 days, using WatchEvent records for 'vinta/awesome-python', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending.

```sql
WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['first_date', 'last_date', 'active_days']`; reference row count: 2.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 2,
    "rows": [
      [
        "2026-10-16",
        "2026-10-19",
        4
      ],
      [
        "2026-10-21",
        "2026-10-21",
        1
      ]
    ],
    "rows_sha256": "1ec5449ef3b54b8b3ec99c7871ac6f2e73cc53afef995627adfc4d194265c90c",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-15",
        "2026-10-19",
        5
      ]
    ],
    "rows_sha256": "620a0602b171efae09f40d528fe2a0a491af67ad1fde0ad2510c923837846389",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 2,
    "rows": [
      [
        "2026-10-14",
        "2026-10-19",
        6
      ],
      [
        "2026-10-21",
        "2026-10-21",
        1
      ]
    ],
    "rows_sha256": "ac70b21aa3a803468a9104220d4d8595d50aa874096858d08c990f316a03c932",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'vinta/awesome-python' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-14",
        "2026-10-19",
        6
      ]
    ],
    "rows_sha256": "b22dbd46bfffaf7d94a0838e3a8399bf1dc52076c1172cc16bcceba07eec8067",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_261 — consecutive_day_runs / distractor

Selection: original_22_identity, replacement_of_reviewed_question.

For previous week, using WatchEvent records for 'codecrafters-io/build-your-own-x', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending. A repository creation year of 2017 is background only and must not filter the answer.

```sql
WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'codecrafters-io/build-your-own-x' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['first_date', 'last_date', 'active_days']`; reference row count: 1.

**REPLACEMENT OF AN ORIGINAL 22-QUESTION REVIEW ID — requires renewed human review.**

Previous question:
For previous week, using PushEvent records for 'electron/electron', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending. A repository creation year of 2017 is background only and must not filter the answer.

Previous reference rows:
```json
[
  [
    "2026-10-08",
    "2026-10-10",
    3
  ],
  [
    "2026-10-12",
    "2026-10-14",
    3
  ]
]
```

Current reference rows:
```json
[
  [
    "2026-10-08",
    "2026-10-14",
    7
  ]
]
```

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND e.repo_name = 'codecrafters-io/build-your-own-x' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-09",
        "2026-10-14",
        6
      ]
    ],
    "rows_sha256": "5e0b90e82eba3f3bb1bf99db76f8574c52e15f3eb899db37c7fa738a139f6c48",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'codecrafters-io/build-your-own-x' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-08",
        "2026-10-13",
        6
      ]
    ],
    "rows_sha256": "2883421a81361ff64295225b86e926d21ab8a512686cab988fb9ebf8974759c7",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'codecrafters-io/build-your-own-x' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-08",
        "2026-10-15",
        8
      ]
    ],
    "rows_sha256": "e2d60d9d58213a85ce08ddb4a0e9ddebb7d96c059b5e3b23d889700ec131c466",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'codecrafters-io/build-your-own-x' AND e.type = 'WatchEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-09",
        "2026-10-15",
        7
      ]
    ],
    "rows_sha256": "0430c4600aa9ebd6ee8ba9ea87b38a160f04b502972b8652fc84b2eacd354c13",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
{
  "appended_line": "Question window: [2026-10-08, 2026-10-15)",
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": true,
  "used_for_filtering": false
}
```

## v4_271 — catalog_lookup / literal

Selection: original_22_identity.

Read the catalog entry for 'github/spec-kit': return repo_name, stars, forks, and open_issues.

```sql
SELECT name AS repo_name, stars, forks, open_issues FROM repos WHERE name = 'github/spec-kit'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_name', 'stars', 'forks', 'open_issues']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_276 — catalog_lookup / distractor

Selection: original_22_identity.

Read the catalog entry for 'github/gitignore': return repo_name, stars, forks, and open_issues. A repository creation year of 2017 is background only and must not filter the answer.

```sql
SELECT name AS repo_name, stars, forks, open_issues FROM repos WHERE name = 'github/gitignore'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_name', 'stars', 'forks', 'open_issues']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
{
  "appended_line": null,
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": false,
  "used_for_filtering": false
}
```

## v4_286 — language_composition / literal

Selection: original_22_identity.

For catalog language 'Batchfile', return repo_count and total_stars summed across its repositories.

```sql
SELECT COUNT(*) AS repo_count, SUM(stars) AS total_stars FROM repos WHERE language = 'Batchfile'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_count', 'total_stars']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_291 — language_composition / distractor

Selection: original_22_identity.

For catalog language 'MDX', return repo_count and total_stars summed across its repositories. A repository creation year of 2017 is background only and must not filter the answer.

```sql
SELECT COUNT(*) AS repo_count, SUM(stars) AS total_stars FROM repos WHERE language = 'MDX'
```

Code-computed boundaries: `None`.
Reference columns: `['repo_count', 'total_stars']`; reference row count: 1.

Glossary original:
```text
No effective time semantics; no time-boundary glossary entry applies.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
{
  "appended_line": null,
  "selection_policy": "leftmost canonical window; decorative standalone years ignored",
  "triggered": false,
  "used_for_filtering": false
}
```

## v4_127 — window_active_contributors / literal

Selection: uncovered_window_expression, stratum=last week x window_active_contributors.

For last week, report active_contributors for repository 'huggingface/transformers' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'huggingface/transformers' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'huggingface/transformers' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        6
      ]
    ],
    "rows_sha256": "a9aa85acf18adf4f2e42f1cb876a854cf82b70587922457d888db0e2df100099",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'huggingface/transformers' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        4
      ]
    ],
    "rows_sha256": "119b714d831408db2dfd9a9ccdade9ed156f595018f81525bcfe504b51097278",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'huggingface/transformers' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        8
      ]
    ],
    "rows_sha256": "c5d72503b693c7a50a114b1610b0a4f187da3be59d0e738fb0b42f5612bd9ea4",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'huggingface/transformers' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        5
      ]
    ],
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_079 — window_collaboration_events / literal

Selection: uncovered_window_expression, stratum=October 8 through October 9, 2026 x window_collaboration_events.

For October 8 through October 9, 2026, report collaboration_events for repository 'openai/codex' as value. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window.

```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-10' AND e.repo_name = 'openai/codex'
```

Code-computed boundaries: `['2026-10-08', '2026-10-10']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-10"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-10' AND e.repo_name = 'openai/codex'",
    "row_count": 1,
    "rows": [
      [
        38
      ]
    ],
    "rows_sha256": "0522347a74657befe54dcfe91998bab26adce04fc17bf628700bf7b0afdc4d50",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-09"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-09' AND e.repo_name = 'openai/codex'",
    "row_count": 1,
    "rows": [
      [
        60
      ]
    ],
    "rows_sha256": "5c61f47670b4291a29f98bb7ad2bdf740a51b16b4ee81d6d6251c5c13de16f73",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-11"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-11' AND e.repo_name = 'openai/codex'",
    "row_count": 1,
    "rows": [
      [
        138
      ]
    ],
    "rows_sha256": "3e4434a6c82e6ad62871f7faa3bcd25304eeef16c6572e785992445f16aa1075",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-11"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-11' AND e.repo_name = 'openai/codex'",
    "row_count": 1,
    "rows": [
      [
        78
      ]
    ],
    "rows_sha256": "08955f26e47cd4037d6f13c1f9ff463c797ab6bca9aefac57f06e9cb0ea3fd53",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-10"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-09"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_262 — consecutive_day_runs / literal

Selection: uncovered_window_expression, stratum=October 8 through October 10, 2026 x consecutive_day_runs.

For October 8 through October 10, 2026, using IssuesEvent records for 'NousResearch/hermes-agent', return every maximal run of consecutive active UTC dates as first_date, last_date, and active_days; a date is active if it contains at least one matching record; order by first_date ascending.

```sql
WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-11' AND e.repo_name = 'NousResearch/hermes-agent' AND e.type = 'IssuesEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-11']`.
Reference columns: `['first_date', 'last_date', 'active_days']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-11"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-11' AND e.repo_name = 'NousResearch/hermes-agent' AND e.type = 'IssuesEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-09",
        "2026-10-10",
        2
      ]
    ],
    "rows_sha256": "22599b6b9ed4cfcf5c0edbc1b448e7df1d496fe307ec93bd5adff417a059176c",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-10"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-10' AND e.repo_name = 'NousResearch/hermes-agent' AND e.type = 'IssuesEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-08",
        "2026-10-09",
        2
      ]
    ],
    "rows_sha256": "bd9ecff53c008ea62276b2920c0633a0cbda6676405c9ef296859dc18c452c9a",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-12"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-12' AND e.repo_name = 'NousResearch/hermes-agent' AND e.type = 'IssuesEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-08",
        "2026-10-11",
        4
      ]
    ],
    "rows_sha256": "d3e5ff43a9531a4e255e7ec05f9a3f2a53af4a3847d2d1968f94297aa99c5e24",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-12"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH active_days AS (SELECT DISTINCT CAST(e.created_at AS DATE) AS day FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-12' AND e.repo_name = 'NousResearch/hermes-agent' AND e.type = 'IssuesEvent'), numbered AS (SELECT day, day - CAST(ROW_NUMBER() OVER (ORDER BY day) AS INTEGER) AS island FROM active_days) SELECT MIN(day) AS first_date, MAX(day) AS last_date, COUNT(*) AS active_days FROM numbered GROUP BY island ORDER BY first_date ASC",
    "row_count": 1,
    "rows": [
      [
        "2026-10-09",
        "2026-10-11",
        3
      ]
    ],
    "rows_sha256": "217d7f52b455b6eaf507d97b3b71d7428014c23271f351a507f202917f64a64d",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-11"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-10"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_031 — window_new_stars / literal

Selection: uncovered_window_expression, stratum=October 8 through October 12, 2026 x window_new_stars.

For October 8 through October 12, 2026, report new_stars for repository 'harry0703/MoneyPrinterTurbo' as value. Count distinct non-null WatchEvent actors, including bots; apply the definition separately per repository within the window.

```sql
SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-13' AND e.repo_name = 'harry0703/MoneyPrinterTurbo'
```

Code-computed boundaries: `['2026-10-08', '2026-10-13']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-13"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-13' AND e.repo_name = 'harry0703/MoneyPrinterTurbo'",
    "row_count": 1,
    "rows": [
      [
        26
      ]
    ],
    "rows_sha256": "a5b1993658848c53c6883104b37606d1db7d6b1a6dbfd1af2c855cc26613311f",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-12"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-12' AND e.repo_name = 'harry0703/MoneyPrinterTurbo'",
    "row_count": 1,
    "rows": [
      [
        22
      ]
    ],
    "rows_sha256": "570e59f0f75c2522415e145e6f64a95a0a4ce65729f7e71e517a4cd71ff4c467",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'harry0703/MoneyPrinterTurbo'",
    "row_count": 1,
    "rows": [
      [
        34
      ]
    ],
    "rows_sha256": "6c96017b4c58bc8ca8a4131843972b7ba1296c6d3b74dd564b55a83faef99f1d",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "SELECT COUNT(DISTINCT CASE WHEN e.type = 'WatchEvent' THEN e.actor END) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'harry0703/MoneyPrinterTurbo'",
    "row_count": 1,
    "rows": [
      [
        29
      ]
    ],
    "rows_sha256": "51cc38ae7f7ec48474a2911c196358ba237244d842eee4f6032d6ad53816d731",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-13"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-12"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_160 — window_active_contributors / literal

Selection: uncovered_window_expression, stratum=October 8 through October 14, 2026 x window_active_contributors.

For October 8 through October 14, 2026, rank up to five 'Dart' repositories with positive active_contributors; return repo_name and value. Order by value descending; break ties by repo_name ascending. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-15' AND r.language = 'Dart' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5
```

Code-computed boundaries: `['2026-10-08', '2026-10-15']`.
Reference columns: `['repo_name', 'value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-15"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-15' AND r.language = 'Dart' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 1,
    "rows": [
      [
        "flutter/flutter",
        3
      ]
    ],
    "rows_sha256": "92da39352a820a7c1febdf36e9ce0bc65aedaaf058b12d9b6dde7b7824e833e0",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-14' AND r.language = 'Dart' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 1,
    "rows": [
      [
        "flutter/flutter",
        2
      ]
    ],
    "rows_sha256": "2eb4db6275a42a1cae2e94a57d7cb1ccd48e41dc75afaa35f6b4391a1e40bd94",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-16' AND r.language = 'Dart' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 1,
    "rows": [
      [
        "flutter/flutter",
        8
      ]
    ],
    "rows_sha256": "96e443aa17c21e1b83fec44057b33fd40037e035c7e635a09fb5f2a8b69efe8d",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH metric AS (WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND r.language = 'Dart' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT repo_name, COUNT(*) AS value FROM qualified GROUP BY repo_name) SELECT repo_name, value FROM metric WHERE value > 0 ORDER BY value DESC, repo_name ASC LIMIT 5",
    "row_count": 1,
    "rows": [
      [
        "flutter/flutter",
        6
      ]
    ],
    "rows_sha256": "5c72455c3e342f63b6943d8d549ee0819408e1e61c9f395ab9ac42e9c8d82de0",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-15"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-14"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_190 — daily_trend / literal

Selection: uncovered_window_expression, stratum=October 8 through October 17, 2026 x daily_trend.

For October 8 through October 17, 2026, using PullRequestEvent records for 'microsoft/vscode', return each UTC date as day and its event_count, including zero-count dates, ordered by day ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-17', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'microsoft/vscode' AND e.type = 'PullRequestEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-18']`.
Reference columns: `['day', 'event_count']`; reference row count: 10.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-18"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-17', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'microsoft/vscode' AND e.type = 'PullRequestEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 9,
    "rows": [
      [
        "2026-10-09",
        5
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        2
      ],
      [
        "2026-10-12",
        2
      ],
      [
        "2026-10-13",
        3
      ],
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        7
      ],
      [
        "2026-10-16",
        9
      ],
      [
        "2026-10-17",
        1
      ]
    ],
    "rows_sha256": "a1f7f83e8bc157dd36d17dfa11b45f685689db49ded7ba20de8a0167369300f3",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-17"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-16', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'microsoft/vscode' AND e.type = 'PullRequestEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 9,
    "rows": [
      [
        "2026-10-08",
        7
      ],
      [
        "2026-10-09",
        5
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        2
      ],
      [
        "2026-10-12",
        2
      ],
      [
        "2026-10-13",
        3
      ],
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        7
      ],
      [
        "2026-10-16",
        9
      ]
    ],
    "rows_sha256": "29705cfdf90d869f72ccb4be4d29379b31ebbcd7718e080fdc60f4b5186ea610",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-19"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-18', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-19' AND e.repo_name = 'microsoft/vscode' AND e.type = 'PullRequestEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 11,
    "rows": [
      [
        "2026-10-08",
        7
      ],
      [
        "2026-10-09",
        5
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        2
      ],
      [
        "2026-10-12",
        2
      ],
      [
        "2026-10-13",
        3
      ],
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        7
      ],
      [
        "2026-10-16",
        9
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        3
      ]
    ],
    "rows_sha256": "1637b472407546632faa73342033c3b5c779ca09fbf66f6020ddd659408c67b2",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-19"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-18', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-19' AND e.repo_name = 'microsoft/vscode' AND e.type = 'PullRequestEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT day, event_count FROM daily ORDER BY day ASC",
    "row_count": 10,
    "rows": [
      [
        "2026-10-09",
        5
      ],
      [
        "2026-10-10",
        0
      ],
      [
        "2026-10-11",
        2
      ],
      [
        "2026-10-12",
        2
      ],
      [
        "2026-10-13",
        3
      ],
      [
        "2026-10-14",
        1
      ],
      [
        "2026-10-15",
        7
      ],
      [
        "2026-10-16",
        9
      ],
      [
        "2026-10-17",
        1
      ],
      [
        "2026-10-18",
        3
      ]
    ],
    "rows_sha256": "8ba830c60852bca2ed89ee7684c38280a6aeb3d0b11f5a83709f66c2ce36184b",
    "start_shift_days": 1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-07",
      "2026-10-18"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-17"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_238 — day_of_week / literal

Selection: uncovered_window_expression, stratum=October 8 through October 21, 2026 x day_of_week.

For October 8 through October 21, 2026, using IssueCommentEvent records for 'golang/go', sum daily counts by weekday (Sunday=0 and Saturday=6) for dates present in the window; return weekday and event_count, including zero-count groups, ordered by weekday ascending.

```sql
WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'golang/go' AND e.type = 'IssueCommentEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC
```

Code-computed boundaries: `['2026-10-08', '2026-10-22']`.
Reference columns: `['weekday', 'event_count']`; reference row count: 7.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-09",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-09', TIMESTAMP '2026-10-21', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'golang/go' AND e.type = 'IssueCommentEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        2
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        2
      ],
      [
        4,
        2
      ],
      [
        5,
        5
      ],
      [
        6,
        9
      ]
    ],
    "rows_sha256": "f627cf60624e6af12a16b5f9c6d7ad577dd75e39483421ac4e8e5f3db3b60539",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-08",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH calendar AS (SELECT CAST(day AS DATE) AS day FROM generate_series(TIMESTAMP '2026-10-08', TIMESTAMP '2026-10-20', INTERVAL '1 day') AS t(day)), counts AS (SELECT CAST(e.created_at AS DATE) AS day, COUNT(*) AS event_count FROM events e WHERE e.created_at >= TIMESTAMP '2026-10-08' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'golang/go' AND e.type = 'IssueCommentEvent' GROUP BY 1), daily AS (SELECT c.day, COALESCE(n.event_count, 0) AS event_count FROM calendar c LEFT JOIN counts n ON c.day = n.day) SELECT EXTRACT(DOW FROM day) AS weekday, SUM(event_count) AS event_count FROM daily GROUP BY 1 ORDER BY weekday ASC",
    "row_count": 7,
    "rows": [
      [
        0,
        2
      ],
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        0
      ],
      [
        4,
        4
      ],
      [
        5,
        5
      ],
      [
        6,
        9
      ]
    ],
    "rows_sha256": "0d99320f5b1ab7cd8da77888b5c8f50de7f799f81e61b16d7d567fb618e7f984",
    "start_shift_days": 0
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-08",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-22"
    ],
    "eligible": false,
    "end_shift_days": 0,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "start_minus_one",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-07",
      "2026-10-21"
    ],
    "eligible": false,
    "end_shift_days": -1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_minus_one",
    "start_shift_days": -1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_115 — window_collaboration_events / literal

Selection: uncovered_window_expression, stratum=October 15 through October 21, 2026 x window_collaboration_events.

For October 15 through October 21, 2026, report collaboration_events for repository 'electron/electron' as value. Count IssuesEvent, PullRequestEvent, and IssueCommentEvent records; apply the definition separately per repository within the window.

```sql
SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'electron/electron'
```

Code-computed boundaries: `['2026-10-15', '2026-10-22']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-16",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-16' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'electron/electron'",
    "row_count": 1,
    "rows": [
      [
        27
      ]
    ],
    "rows_sha256": "998722f22406bf9327db937d41ade9add04b5c840b15208ea307d8f797bbf5f9",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-15",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-15' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'electron/electron'",
    "row_count": 1,
    "rows": [
      [
        43
      ]
    ],
    "rows_sha256": "c10092b6a60348028cec782ee9d75b6d1f6e9e48044d1b6e3db13da529467a2f",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-22"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-22' AND e.repo_name = 'electron/electron'",
    "row_count": 1,
    "rows": [
      [
        57
      ]
    ],
    "rows_sha256": "1d356977cc585cf151d608bd70b49a5b88deb2b79df08a7070a892be8348d01e",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-14",
      "2026-10-21"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "SELECT COUNT(*) FILTER (WHERE e.type IN ('IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent')) AS value FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-14' AND e.created_at < TIMESTAMP '2026-10-21' AND e.repo_name = 'electron/electron'",
    "row_count": 1,
    "rows": [
      [
        52
      ]
    ],
    "rows_sha256": "4a15a2c33bb4c1ec17cb02032ce4c3cbf6a0de5db5f7dcb6d74a6c7ee4aae755",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[
  {
    "bounds": [
      "2026-10-15",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "end_plus_one",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-16",
      "2026-10-23"
    ],
    "eligible": false,
    "end_shift_days": 1,
    "exclusion_reason": "outside_snapshot_coverage",
    "perturbation": "both_plus_one",
    "start_shift_days": 1
  }
]
```

Distractor injection probe:
```json
null
```

## v4_139 — window_active_contributors / literal

Selection: uncovered_window_expression, stratum=October 11 through October 12, 2026 x window_active_contributors.

For October 11 through October 12, 2026, report active_contributors for repository 'langgenius/dify' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-13' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-11', '2026-10-13']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-12",
      "2026-10-13"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-12' AND e.created_at < TIMESTAMP '2026-10-13' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        2
      ]
    ],
    "rows_sha256": "24227028f5989317de063afa979c6b34bfd191537b8fd2ed796a820bf47b2024",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-11",
      "2026-10-12"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-12' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        0
      ]
    ],
    "rows_sha256": "db407f11d7ede59abaab0e98e097ff2dae10a048207b801745d7199ef19c2387",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-11",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        5
      ]
    ],
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-13"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-13' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        5
      ]
    ],
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-12",
      "2026-10-14"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-12' AND e.created_at < TIMESTAMP '2026-10-14' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        5
      ]
    ],
    "rows_sha256": "77471ebe3613f4714666523fa961eb443f57dc2396a31528afdbbea86fadc8f8",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-12"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-12' AND e.repo_name = 'langgenius/dify' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        2
      ]
    ],
    "rows_sha256": "24227028f5989317de063afa979c6b34bfd191537b8fd2ed796a820bf47b2024",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_157 — window_active_contributors / literal

Selection: uncovered_window_expression, stratum=October 10 through October 16, 2026 x window_active_contributors.

For October 10 through October 16, 2026, report active_contributors for repository 'openclaw/openclaw' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-10', '2026-10-17']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-11",
      "2026-10-17"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-18"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        16
      ]
    ],
    "rows_sha256": "d031a2f52c936db4b9052d4524fecb03b6b3be0e28a75fe2ddfd3d7ebc613c57",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-17"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        15
      ]
    ],
    "rows_sha256": "bc54a496c58cd6946984014c34865e5dcc1443494b29dce0c089e80f4690c9c7",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-11",
      "2026-10-18"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        15
      ]
    ],
    "rows_sha256": "bc54a496c58cd6946984014c34865e5dcc1443494b29dce0c089e80f4690c9c7",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-09",
      "2026-10-16"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-09' AND e.created_at < TIMESTAMP '2026-10-16' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
null
```

## v4_175 — window_active_contributors / literal

Selection: uncovered_window_expression, stratum=October 11 through October 17, 2026 x window_active_contributors.

For October 11 through October 17, 2026, report active_contributors for repository 'openclaw/openclaw' as value. Count non-null actors with at least three PushEvent, IssuesEvent, PullRequestEvent, or IssueCommentEvent records, excluding case-insensitive [bot] suffixes; apply the definition separately per repository within the window.

```sql
WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified
```

Code-computed boundaries: `['2026-10-11', '2026-10-18']`.
Reference columns: `['value']`; reference row count: 1.

Glossary original:
```text
- All timestamps are UTC. The `created_at` columns are stored as UTC.
- `reference_date` = **2026-10-22**. Every question treats this date as "today".
  Always write it as a literal (`DATE '2026-10-22'` / `TIMESTAMP '2026-10-22 00:00:00'`).
  Never use `CURRENT_DATE` or `CURRENT_TIMESTAMP`; the dataset is a frozen snapshot.
- Time windows are half-open intervals: `created_at >= start AND created_at < end`.
- "The last 7 days" means the 7 full UTC days before `reference_date`:
  `2026-10-15 00:00:00 <= created_at < 2026-10-22 00:00:00`.
- An explicit range like "October 8 through October 21, 2026" means
  `2026-10-08 00:00:00 <= created_at < 2026-10-22 00:00:00` (end date inclusive, so the
  exclusive bound is the next day).
- "Previous week" vs "last week": previous = Oct 8–14, last = Oct 15–21 (both UTC).
- A "UTC date" of an event is `CAST(created_at AS DATE)`.
```

Manual worksheet (leave blank):

| Item | Reviewer calculation |
| --- | --- |
| Inclusive start | |
| Inclusive final date | |
| Exclusive end | |
| UTC / reference-date check | |
| Agreement and reviewer initials | |

Eligible sensitivity evidence:
```json
[
  {
    "bounds": [
      "2026-10-12",
      "2026-10-18"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-12' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-11",
      "2026-10-17"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "end_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        13
      ]
    ],
    "rows_sha256": "eeabd8e733b414a73deef88047a3ea68d22640191cf5f6c793d5389fc5ef3a7f",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-11",
      "2026-10-19"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "end_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-11' AND e.created_at < TIMESTAMP '2026-10-19' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        20
      ]
    ],
    "rows_sha256": "f2715dd605b7502ff4d35ec4613d864a78786d7bb2b73cd9cca0ca76ee5777c9",
    "start_shift_days": 0
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-18"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 0,
    "exclusion_reason": null,
    "perturbation": "start_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-18' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        16
      ]
    ],
    "rows_sha256": "d031a2f52c936db4b9052d4524fecb03b6b3be0e28a75fe2ddfd3d7ebc613c57",
    "start_shift_days": -1
  },
  {
    "bounds": [
      "2026-10-12",
      "2026-10-19"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": 1,
    "exclusion_reason": null,
    "perturbation": "both_plus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-12' AND e.created_at < TIMESTAMP '2026-10-19' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        17
      ]
    ],
    "rows_sha256": "bea0e0959fc3488f007700fe40dfdcfd4cdd9c91c817fac17f25df5ef4063846",
    "start_shift_days": 1
  },
  {
    "bounds": [
      "2026-10-10",
      "2026-10-17"
    ],
    "changed": true,
    "eligible": true,
    "end_shift_days": -1,
    "exclusion_reason": null,
    "perturbation": "both_minus_one",
    "reference_sql": "WITH qualified AS (SELECT e.repo_name, e.actor FROM events e JOIN repos r ON r.repo_id = e.repo_id WHERE e.created_at >= TIMESTAMP '2026-10-10' AND e.created_at < TIMESTAMP '2026-10-17' AND e.repo_name = 'openclaw/openclaw' AND e.actor IS NOT NULL AND LOWER(e.actor) NOT LIKE '%[bot]' AND e.type IN ('PushEvent', 'IssuesEvent', 'PullRequestEvent', 'IssueCommentEvent') GROUP BY e.repo_name, e.actor HAVING COUNT(*) >= 3) SELECT COUNT(*) AS value FROM qualified",
    "row_count": 1,
    "rows": [
      [
        14
      ]
    ],
    "rows_sha256": "00a3ab2bdd368fd8b5ed2d04bd53935d588c773800da5e9cca45b88737039808",
    "start_shift_days": -1
  }
]
```

Excluded perturbations (not executed):
```json
[]
```

Distractor injection probe:
```json
null
```
