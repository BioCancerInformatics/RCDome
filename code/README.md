# RCDome — Project-wide code catalog (V027)

Every analysis family and its scripts, grouped by folder under `code/`.
Generated from the actual files in the repository.

## adjudication/  (11 scripts)

- `add_mapped_vote_columns.R`
- `adjudication_53.py`
- `append_pmids_to_references.py`
- `build_matrix_additive_columns.py`
- `count_pmids_v027.py`
- `fetch_verbatim_agreement.py`
- `fix_v025_rds_2rows.R`
- `fix_vcd_rds.R`
- `precompute_disc_df.R`
- `precompute_disc_html.R`
- `split_mapped_votes.R`

## audits/  (19 scripts)

- `audit_final_compliance_AB.py`
- `audit_groupA_ocean_deep.py`
- `audit_ocean_deep.py`
- `audit_ultimate_granular.py`
- `audit_victor_compliance.py`
- `audit_victor_compliance_final.py`
- `compliance_audit.py`
- `deepest_app_audit.py`
- `final_review_77.py`
- `fix_victor_app_report_2026-09-19.py`
- `full_manuscript_conformity_audit.py`
- `global_conformity_audit.py`
- `higor_compliance_audit.py`
- `higor_propagation_audit.py`
- `manuscript_conformity_audit.py`
- `manuscript_v026_deep_audit.py`
- `reconcile_groupA_decoder_board.py`
- `resource_claims.py`
- `supplementary_tables_diff.py`

## benchmarks/  (22 scripts)

- `benchmark_heldout_20260919.R`
- `benchmark_reference_discipline.R`
- `benchmark_t06_context_fidelity.R`
- `consensus_benchmark_agnostic.py`
- `consensus_benchmark_reference.py`
- `consensus_benchmark_reference_v2.py`
- `consensus_benchmark_reference_v3.py`
- `consensus_benchmark_reference_v4.py`
- `consensus_benchmark_v5_combined.py`
- `consensus_benchmark_v6_v11loop.py`
- `consensus_benchmark_v7_neutral_query.py`
- `cot_benchmark.py`
- `cot_benchmark_v10.py`
- `cot_benchmark_v11.py`
- `cot_benchmark_v2.py`
- `cot_benchmark_v3.py`
- `cot_benchmark_v4.py`
- `cot_benchmark_v5.py`
- `cot_benchmark_v6.py`
- `cot_benchmark_v7.py`
- `cot_benchmark_v8.py`
- `cot_benchmark_v9.py`

## classification/  (4 scripts)

- `phase2ad_mini_2pairs.py`
- `stage2_classify.py`
- `stage2_pass2.py`
- `stage2_pass3_semantic.py`

## decoder/  (33 scripts)

- `add_provenance.py`
- `add_rodrigues_complement.py`
- `apply_galluzzi_format.py`
- `build_decoder_53.py`
- `build_variable_descriptor.py`
- `consensus_crossvalidate.py`
- `consensus_deep_search.py`
- `deep_audit.py`
- `deepest_app_audit.py`
- `final_ocean_audit.py`
- `final_readiness_audit.py`
- `fix_nccd_complements.py`
- `founding_pmid_lookup.py`
- `full_manuscript_conformity_audit.py`
- `global_conformity_audit.py`
- `governance_checker.py`
- `inject_od_subsections.py`
- `insert_figure1_legend.py`
- `make_review_worksheet.py`
- `manuscript_conformity_audit.py`
- `merge_approved.py`
- `pmid_topic_audit.py`
- `recover_fulltexts.py`
- `renumber_tables_S.py`
- `run_board_benchmark.py`
- `scoring_formulas.py`
- `smoke_test.py`
- `standardize_citations.py`
- `sync_to_github.py`
- `validate_od_consensus.py`
- `validate_od_deepseek.py`
- `validate_od_fulltext.py`
- `verbatim_audit.py`

## distribution/  (5 scripts)

- `build_distribution.py`
- `build_github_mirror.py`
- `generate_detail_page.py`
- `make_v025_zip.py`
- `make_v026_zip.py`

## extraction/  (90 scripts)

- `add_rcdome_ontology.py`
- `audit_phase2b.py`
- `audit_phase3.py`
- `benchmark_phase2b.py`
- `benchmark_phase3.py`
- `channel_2e_zero_pmid_recovery.py`
- `channel_a_rodrigues2025.py`
- `channel_b_atd.py`
- `channel_b_ferrdb_v3.py`
- `channel_b_go.py`
- `channel_b_hadb.py`
- `channel_b_hamdb.py`
- `channel_b_ilir.py`
- `channel_b_ipcd.py`
- `channel_b_kegg.py`
- `channel_b_lncrcd.py`
- `channel_b_msigdb.py`
- `channel_b_ncbi_gene.py`
- `channel_b_phase2_new_forms.py`
- `channel_b_rcddb.py`
- `channel_b_reactome.py`
- `channel_b_xdeathdb.py`
- `channel_c_evidence_tier.py`
- `channel_c_recovery_europe_pmc.py`
- `channel_e_elicit_extract.py`
- `channel_e_elicit_extract_benchmark_50.py`
- `check_sessions_csv.py`
- `check_test_session.py`
- `check_triaptosis.py`
- `compare_capped_uncapped.py`
- `complete_recovery.py`
- `cot_benchmark.py`
- `cot_benchmark_v10.py`
- `cot_benchmark_v11.py`
- `cot_benchmark_v2.py`
- `cot_benchmark_v3.py`
- `cot_benchmark_v4.py`
- `cot_benchmark_v5.py`
- `cot_benchmark_v6.py`
- `cot_benchmark_v7.py`
- `cot_benchmark_v8.py`
- `cot_benchmark_v9.py`
- `cot_pilot.py`
- `cot_pilot_rescue.py`
- `count_genes_uncapped.py`
- `debug_curl.py`
- `deepseek_cot_full.py`
- `deepseek_cot_mini_2pairs.py`
- `deepseek_cot_v11_full.py`
- `download_extract.py`
- `download_phase2b_ris.py`
- `elicit_fulltext_6.py`
- `elicit_fulltext_test.py`
- `elicit_semantic_search_8genes.py`
- `elicit_targeted_17.py`
- `extract_governance_literature.py`
- `fill_100_500_gaps.py`
- `fix_progress.py`
- `governance_collapse.py`
- `governance_final_collapse.py`
- `governance_finalize.py`
- `governance_merge_v2.py`
- `governance_theme_synthesis.py`
- `governed_count_uncapped.py`
- `inspect_session_structure.py`
- `master_extract.py`
- `merge_cot_into_matrix.py`
- `merge_engine.py`
- `merge_phase2d_results.py`
- `notify_email.py`
- `phase2ad_msigdb_1832.py`
- `phase2ad_residual.py`
- `phase3b_p1.py`
- `phase3b_p2.py`
- `phase3b_p3.py`
- `phase3b_p4_RegulatedNecrosis.py`
- `recheck_500.py`
- `recheck_500_v2.py`
- `recover_3_sessions.py`
- `save_matrix_excel_rds.R`
- `test_apoptosis_small.py`
- `test_maxresults_cap.py`
- `test_pro_cap_1000.py`
- `test_uncapped_elicit.py`
- `utility_apply_qc.py`
- `utility_convert_to_docx.py`
- `utility_map_uniprot.py`
- `utility_normalize_rcd_forms.py`
- `utility_validate_hgnc.py`
- `verify_rows_vs_papers.py`

## figures/  (15 scripts)

- `generate_rcdome_flowchart.R`
- `make_figure1_flowchart.py`
- `make_figure3_composite.py`
- `make_figure4.py`
- `make_figure4_pdf.py`
- `make_figure4_v2.py`
- `make_figure4_v3.py`
- `make_figure_db_contribution.R`
- `make_figure_entity_coverage.R`
- `make_figure_entity_coverage.py`
- `make_figure_s2_stacked_by_level.py`
- `make_figure_s3_stacked_by_level.py`
- `make_figure_source_classification.R`
- `make_infographic_EN.py`
- `translate_infographic_EN.py`

## manuscript/  (22 scripts)

- `add_front_page.py`
- `add_supplementary_legends.py`
- `edit_manuscript_structure.py`
- `edit_manuscript_structure_2.py`
- `fix_figure_references.py`
- `fix_phase2c_and_heading.py`
- `fix_supplementary_tables.py`
- `insert_figure1_legend.py`
- `insert_figure2_legend.py`
- `insert_figure4_legend.py`
- `make_variable_dictionary.py`
- `merge_supplementary_notes.py`
- `rebuild_notes.py`
- `recompute_results_counts.py`
- `reduce_emdashes.py`
- `reindex_elicit_gene_symbol.py`
- `renumber_supp_figures.py`
- `renumber_supp_figures_universal.py`
- `reorder_phase23.py`
- `reorder_phase2g.py`
- `replace_figure_legends.py`
- `uniformize_supplementary.py`

## merge/  (3 scripts)

- `merge_cot_into_matrix.py`
- `merge_engine.py`
- `merge_phase2d_results.py`

## other/  (5 scripts)

- `RScript - Classifying and prioritizing immunotherapy genes by roles on RCD.R`
- `capture_gene_catalog.py`
- `capture_raw_views.py`
- `g5_worksheet.py`
- `update_traceability.py`

## retrieval/  (9 scripts)

- `broader_sweep.py`
- `extract_claims_and_cache.py`
- `fetch_gene_summaries.py`
- `pa0_ocean.py`
- `pa0_rescan.py`
- `pa0_residual.py`
- `reanchor_claims.py`
- `triage_not_supported.py`
- `verify_claim_fulltext.py`

## surveillance/  (1 scripts)

- `surveillance_preprint_rcd_terms.py`

## tests/  (4 scripts)

- `test_app_full_drive.py`
- `test_app_modules.py`
- `test_app_smoke.py`
- `test_app_smoke_v027.py`

## validation/  (6 scripts)

- `channel_c_evidence_tier.py`
- `channel_c_recovery_europe_pmc.py`
- `consensus_cot_full.py`
- `deepseek_cot_v11_full.py`
- `phase2ad_msigdb_1832.py`
- `phase2ad_residual.py`

**Total: 249 scripts across 15 families.**