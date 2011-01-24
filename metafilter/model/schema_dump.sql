--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- Name: lquery; Type: SHELL TYPE; Schema: public; Owner: postgres
--

CREATE TYPE lquery;


--
-- Name: lquery_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lquery_in(cstring) RETURNS lquery
    AS '$libdir/ltree', 'lquery_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.lquery_in(cstring) OWNER TO postgres;

--
-- Name: lquery_out(lquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lquery_out(lquery) RETURNS cstring
    AS '$libdir/ltree', 'lquery_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.lquery_out(lquery) OWNER TO postgres;

--
-- Name: lquery; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE lquery (
    INTERNALLENGTH = variable,
    INPUT = lquery_in,
    OUTPUT = lquery_out,
    ALIGNMENT = int4,
    STORAGE = extended
);


ALTER TYPE public.lquery OWNER TO postgres;

--
-- Name: ltree; Type: SHELL TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltree;


--
-- Name: ltree_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_in(cstring) RETURNS ltree
    AS '$libdir/ltree', 'ltree_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltree_in(cstring) OWNER TO postgres;

--
-- Name: ltree_out(ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_out(ltree) RETURNS cstring
    AS '$libdir/ltree', 'ltree_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltree_out(ltree) OWNER TO postgres;

--
-- Name: ltree; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltree (
    INTERNALLENGTH = variable,
    INPUT = ltree_in,
    OUTPUT = ltree_out,
    ALIGNMENT = int4,
    STORAGE = extended
);


ALTER TYPE public.ltree OWNER TO postgres;

--
-- Name: ltree_gist; Type: SHELL TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltree_gist;


--
-- Name: ltree_gist_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_gist_in(cstring) RETURNS ltree_gist
    AS '$libdir/ltree', 'ltree_gist_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltree_gist_in(cstring) OWNER TO postgres;

--
-- Name: ltree_gist_out(ltree_gist); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_gist_out(ltree_gist) RETURNS cstring
    AS '$libdir/ltree', 'ltree_gist_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltree_gist_out(ltree_gist) OWNER TO postgres;

--
-- Name: ltree_gist; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltree_gist (
    INTERNALLENGTH = variable,
    INPUT = ltree_gist_in,
    OUTPUT = ltree_gist_out,
    ALIGNMENT = int4,
    STORAGE = plain
);


ALTER TYPE public.ltree_gist OWNER TO postgres;

--
-- Name: ltxtquery; Type: SHELL TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltxtquery;


--
-- Name: ltxtq_in(cstring); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltxtq_in(cstring) RETURNS ltxtquery
    AS '$libdir/ltree', 'ltxtq_in'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltxtq_in(cstring) OWNER TO postgres;

--
-- Name: ltxtq_out(ltxtquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltxtq_out(ltxtquery) RETURNS cstring
    AS '$libdir/ltree', 'ltxtq_out'
    LANGUAGE c STRICT;


ALTER FUNCTION public.ltxtq_out(ltxtquery) OWNER TO postgres;

--
-- Name: ltxtquery; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE ltxtquery (
    INTERNALLENGTH = variable,
    INPUT = ltxtq_in,
    OUTPUT = ltxtq_out,
    ALIGNMENT = int4,
    STORAGE = extended
);


ALTER TYPE public.ltxtquery OWNER TO postgres;

--
-- Name: _lt_q_regex(ltree[], lquery[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _lt_q_regex(ltree[], lquery[]) RETURNS boolean
    AS '$libdir/ltree', '_lt_q_regex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._lt_q_regex(ltree[], lquery[]) OWNER TO postgres;

--
-- Name: _lt_q_rregex(lquery[], ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _lt_q_rregex(lquery[], ltree[]) RETURNS boolean
    AS '$libdir/ltree', '_lt_q_rregex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._lt_q_rregex(lquery[], ltree[]) OWNER TO postgres;

--
-- Name: _ltq_extract_regex(ltree[], lquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltq_extract_regex(ltree[], lquery) RETURNS ltree
    AS '$libdir/ltree', '_ltq_extract_regex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltq_extract_regex(ltree[], lquery) OWNER TO postgres;

--
-- Name: _ltq_regex(ltree[], lquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltq_regex(ltree[], lquery) RETURNS boolean
    AS '$libdir/ltree', '_ltq_regex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltq_regex(ltree[], lquery) OWNER TO postgres;

--
-- Name: _ltq_rregex(lquery, ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltq_rregex(lquery, ltree[]) RETURNS boolean
    AS '$libdir/ltree', '_ltq_rregex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltq_rregex(lquery, ltree[]) OWNER TO postgres;

--
-- Name: _ltree_compress(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_compress(internal) RETURNS internal
    AS '$libdir/ltree', '_ltree_compress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public._ltree_compress(internal) OWNER TO postgres;

--
-- Name: _ltree_consistent(internal, internal, smallint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_consistent(internal, internal, smallint) RETURNS boolean
    AS '$libdir/ltree', '_ltree_consistent'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public._ltree_consistent(internal, internal, smallint) OWNER TO postgres;

--
-- Name: _ltree_extract_isparent(ltree[], ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_extract_isparent(ltree[], ltree) RETURNS ltree
    AS '$libdir/ltree', '_ltree_extract_isparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_extract_isparent(ltree[], ltree) OWNER TO postgres;

--
-- Name: _ltree_extract_risparent(ltree[], ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_extract_risparent(ltree[], ltree) RETURNS ltree
    AS '$libdir/ltree', '_ltree_extract_risparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_extract_risparent(ltree[], ltree) OWNER TO postgres;

--
-- Name: _ltree_isparent(ltree[], ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_isparent(ltree[], ltree) RETURNS boolean
    AS '$libdir/ltree', '_ltree_isparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_isparent(ltree[], ltree) OWNER TO postgres;

--
-- Name: _ltree_penalty(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_penalty(internal, internal, internal) RETURNS internal
    AS '$libdir/ltree', '_ltree_penalty'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_penalty(internal, internal, internal) OWNER TO postgres;

--
-- Name: _ltree_picksplit(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_picksplit(internal, internal) RETURNS internal
    AS '$libdir/ltree', '_ltree_picksplit'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public._ltree_picksplit(internal, internal) OWNER TO postgres;

--
-- Name: _ltree_r_isparent(ltree, ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_r_isparent(ltree, ltree[]) RETURNS boolean
    AS '$libdir/ltree', '_ltree_r_isparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_r_isparent(ltree, ltree[]) OWNER TO postgres;

--
-- Name: _ltree_r_risparent(ltree, ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_r_risparent(ltree, ltree[]) RETURNS boolean
    AS '$libdir/ltree', '_ltree_r_risparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_r_risparent(ltree, ltree[]) OWNER TO postgres;

--
-- Name: _ltree_risparent(ltree[], ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_risparent(ltree[], ltree) RETURNS boolean
    AS '$libdir/ltree', '_ltree_risparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltree_risparent(ltree[], ltree) OWNER TO postgres;

--
-- Name: _ltree_same(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_same(internal, internal, internal) RETURNS internal
    AS '$libdir/ltree', '_ltree_same'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public._ltree_same(internal, internal, internal) OWNER TO postgres;

--
-- Name: _ltree_union(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltree_union(internal, internal) RETURNS integer
    AS '$libdir/ltree', '_ltree_union'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public._ltree_union(internal, internal) OWNER TO postgres;

--
-- Name: _ltxtq_exec(ltree[], ltxtquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltxtq_exec(ltree[], ltxtquery) RETURNS boolean
    AS '$libdir/ltree', '_ltxtq_exec'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltxtq_exec(ltree[], ltxtquery) OWNER TO postgres;

--
-- Name: _ltxtq_extract_exec(ltree[], ltxtquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltxtq_extract_exec(ltree[], ltxtquery) RETURNS ltree
    AS '$libdir/ltree', '_ltxtq_extract_exec'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltxtq_extract_exec(ltree[], ltxtquery) OWNER TO postgres;

--
-- Name: _ltxtq_rexec(ltxtquery, ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION _ltxtq_rexec(ltxtquery, ltree[]) RETURNS boolean
    AS '$libdir/ltree', '_ltxtq_rexec'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._ltxtq_rexec(ltxtquery, ltree[]) OWNER TO postgres;

--
-- Name: index(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION index(ltree, ltree) RETURNS integer
    AS '$libdir/ltree', 'ltree_index'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.index(ltree, ltree) OWNER TO postgres;

--
-- Name: index(ltree, ltree, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION index(ltree, ltree, integer) RETURNS integer
    AS '$libdir/ltree', 'ltree_index'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.index(ltree, ltree, integer) OWNER TO postgres;

--
-- Name: lca(ltree[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree[]) RETURNS ltree
    AS '$libdir/ltree', '_lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree[]) OWNER TO postgres;

--
-- Name: lca(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree, ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree, ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree, ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'lca'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lca(ltree, ltree, ltree, ltree, ltree, ltree, ltree, ltree) OWNER TO postgres;

--
-- Name: lt_q_regex(ltree, lquery[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lt_q_regex(ltree, lquery[]) RETURNS boolean
    AS '$libdir/ltree', 'lt_q_regex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lt_q_regex(ltree, lquery[]) OWNER TO postgres;

--
-- Name: lt_q_rregex(lquery[], ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION lt_q_rregex(lquery[], ltree) RETURNS boolean
    AS '$libdir/ltree', 'lt_q_rregex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.lt_q_rregex(lquery[], ltree) OWNER TO postgres;

--
-- Name: ltq_regex(ltree, lquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltq_regex(ltree, lquery) RETURNS boolean
    AS '$libdir/ltree', 'ltq_regex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltq_regex(ltree, lquery) OWNER TO postgres;

--
-- Name: ltq_rregex(lquery, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltq_rregex(lquery, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltq_rregex'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltq_rregex(lquery, ltree) OWNER TO postgres;

--
-- Name: ltree2text(ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree2text(ltree) RETURNS text
    AS '$libdir/ltree', 'ltree2text'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree2text(ltree) OWNER TO postgres;

--
-- Name: ltree_addltree(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_addltree(ltree, ltree) RETURNS ltree
    AS '$libdir/ltree', 'ltree_addltree'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_addltree(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_addtext(ltree, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_addtext(ltree, text) RETURNS ltree
    AS '$libdir/ltree', 'ltree_addtext'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_addtext(ltree, text) OWNER TO postgres;

--
-- Name: ltree_cmp(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_cmp(ltree, ltree) RETURNS integer
    AS '$libdir/ltree', 'ltree_cmp'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_cmp(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_compress(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_compress(internal) RETURNS internal
    AS '$libdir/ltree', 'ltree_compress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_compress(internal) OWNER TO postgres;

--
-- Name: ltree_consistent(internal, internal, smallint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_consistent(internal, internal, smallint) RETURNS boolean
    AS '$libdir/ltree', 'ltree_consistent'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_consistent(internal, internal, smallint) OWNER TO postgres;

--
-- Name: ltree_decompress(internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_decompress(internal) RETURNS internal
    AS '$libdir/ltree', 'ltree_decompress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_decompress(internal) OWNER TO postgres;

--
-- Name: ltree_eq(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_eq(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_eq'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_eq(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_ge(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_ge(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_ge'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_ge(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_gt(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_gt(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_gt'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_gt(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_isparent(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_isparent(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_isparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_isparent(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_le(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_le(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_le'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_le(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_lt(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_lt(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_lt'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_lt(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_ne(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_ne(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_ne'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_ne(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_penalty(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_penalty(internal, internal, internal) RETURNS internal
    AS '$libdir/ltree', 'ltree_penalty'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_penalty(internal, internal, internal) OWNER TO postgres;

--
-- Name: ltree_picksplit(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_picksplit(internal, internal) RETURNS internal
    AS '$libdir/ltree', 'ltree_picksplit'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_picksplit(internal, internal) OWNER TO postgres;

--
-- Name: ltree_risparent(ltree, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_risparent(ltree, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltree_risparent'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_risparent(ltree, ltree) OWNER TO postgres;

--
-- Name: ltree_same(internal, internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_same(internal, internal, internal) RETURNS internal
    AS '$libdir/ltree', 'ltree_same'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_same(internal, internal, internal) OWNER TO postgres;

--
-- Name: ltree_textadd(text, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_textadd(text, ltree) RETURNS ltree
    AS '$libdir/ltree', 'ltree_textadd'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltree_textadd(text, ltree) OWNER TO postgres;

--
-- Name: ltree_union(internal, internal); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltree_union(internal, internal) RETURNS integer
    AS '$libdir/ltree', 'ltree_union'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ltree_union(internal, internal) OWNER TO postgres;

--
-- Name: ltreeparentsel(internal, oid, internal, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltreeparentsel(internal, oid, internal, integer) RETURNS double precision
    AS '$libdir/ltree', 'ltreeparentsel'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltreeparentsel(internal, oid, internal, integer) OWNER TO postgres;

--
-- Name: ltxtq_exec(ltree, ltxtquery); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltxtq_exec(ltree, ltxtquery) RETURNS boolean
    AS '$libdir/ltree', 'ltxtq_exec'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltxtq_exec(ltree, ltxtquery) OWNER TO postgres;

--
-- Name: ltxtq_rexec(ltxtquery, ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION ltxtq_rexec(ltxtquery, ltree) RETURNS boolean
    AS '$libdir/ltree', 'ltxtq_rexec'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.ltxtq_rexec(ltxtquery, ltree) OWNER TO postgres;

--
-- Name: nlevel(ltree); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION nlevel(ltree) RETURNS integer
    AS '$libdir/ltree', 'nlevel'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.nlevel(ltree) OWNER TO postgres;

--
-- Name: subltree(ltree, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION subltree(ltree, integer, integer) RETURNS ltree
    AS '$libdir/ltree', 'subltree'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.subltree(ltree, integer, integer) OWNER TO postgres;

--
-- Name: subpath(ltree, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION subpath(ltree, integer, integer) RETURNS ltree
    AS '$libdir/ltree', 'subpath'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.subpath(ltree, integer, integer) OWNER TO postgres;

--
-- Name: subpath(ltree, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION subpath(ltree, integer) RETURNS ltree
    AS '$libdir/ltree', 'subpath'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.subpath(ltree, integer) OWNER TO postgres;

--
-- Name: text2ltree(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION text2ltree(text) RETURNS ltree
    AS '$libdir/ltree', 'text2ltree'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.text2ltree(text) OWNER TO postgres;

--
-- Name: <; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR < (
    PROCEDURE = ltree_lt,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = >,
    NEGATOR = >=,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.< (ltree, ltree) OWNER TO postgres;

--
-- Name: <=; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <= (
    PROCEDURE = ltree_le,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = >=,
    NEGATOR = >,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<= (ltree, ltree) OWNER TO postgres;

--
-- Name: <>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <> (
    PROCEDURE = ltree_ne,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = <>,
    NEGATOR = =,
    RESTRICT = neqsel,
    JOIN = neqjoinsel
);


ALTER OPERATOR public.<> (ltree, ltree) OWNER TO postgres;

--
-- Name: <@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <@ (
    PROCEDURE = ltree_risparent,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = @>,
    RESTRICT = ltreeparentsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<@ (ltree, ltree) OWNER TO postgres;

--
-- Name: <@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <@ (
    PROCEDURE = _ltree_r_isparent,
    LEFTARG = ltree,
    RIGHTARG = ltree[],
    COMMUTATOR = @>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<@ (ltree, ltree[]) OWNER TO postgres;

--
-- Name: <@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR <@ (
    PROCEDURE = _ltree_risparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree,
    COMMUTATOR = @>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<@ (ltree[], ltree) OWNER TO postgres;

--
-- Name: =; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR = (
    PROCEDURE = ltree_eq,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = =,
    NEGATOR = <>,
    MERGES,
    RESTRICT = eqsel,
    JOIN = eqjoinsel
);


ALTER OPERATOR public.= (ltree, ltree) OWNER TO postgres;

--
-- Name: >; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR > (
    PROCEDURE = ltree_gt,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = <,
    NEGATOR = <=,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.> (ltree, ltree) OWNER TO postgres;

--
-- Name: >=; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR >= (
    PROCEDURE = ltree_ge,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = <=,
    NEGATOR = <,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.>= (ltree, ltree) OWNER TO postgres;

--
-- Name: ?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ? (
    PROCEDURE = lt_q_rregex,
    LEFTARG = lquery[],
    RIGHTARG = ltree,
    COMMUTATOR = ?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.? (lquery[], ltree) OWNER TO postgres;

--
-- Name: ?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ? (
    PROCEDURE = lt_q_regex,
    LEFTARG = ltree,
    RIGHTARG = lquery[],
    COMMUTATOR = ?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.? (ltree, lquery[]) OWNER TO postgres;

--
-- Name: ?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ? (
    PROCEDURE = _lt_q_rregex,
    LEFTARG = lquery[],
    RIGHTARG = ltree[],
    COMMUTATOR = ?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.? (lquery[], ltree[]) OWNER TO postgres;

--
-- Name: ?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ? (
    PROCEDURE = _lt_q_regex,
    LEFTARG = ltree[],
    RIGHTARG = lquery[],
    COMMUTATOR = ?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.? (ltree[], lquery[]) OWNER TO postgres;

--
-- Name: ?<@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ?<@ (
    PROCEDURE = _ltree_extract_risparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree
);


ALTER OPERATOR public.?<@ (ltree[], ltree) OWNER TO postgres;

--
-- Name: ?@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ?@ (
    PROCEDURE = _ltxtq_extract_exec,
    LEFTARG = ltree[],
    RIGHTARG = ltxtquery
);


ALTER OPERATOR public.?@ (ltree[], ltxtquery) OWNER TO postgres;

--
-- Name: ?@>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ?@> (
    PROCEDURE = _ltree_extract_isparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree
);


ALTER OPERATOR public.?@> (ltree[], ltree) OWNER TO postgres;

--
-- Name: ?~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ?~ (
    PROCEDURE = _ltq_extract_regex,
    LEFTARG = ltree[],
    RIGHTARG = lquery
);


ALTER OPERATOR public.?~ (ltree[], lquery) OWNER TO postgres;

--
-- Name: @; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @ (
    PROCEDURE = ltxtq_rexec,
    LEFTARG = ltxtquery,
    RIGHTARG = ltree,
    COMMUTATOR = @,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@ (ltxtquery, ltree) OWNER TO postgres;

--
-- Name: @; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @ (
    PROCEDURE = ltxtq_exec,
    LEFTARG = ltree,
    RIGHTARG = ltxtquery,
    COMMUTATOR = @,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@ (ltree, ltxtquery) OWNER TO postgres;

--
-- Name: @; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @ (
    PROCEDURE = _ltxtq_rexec,
    LEFTARG = ltxtquery,
    RIGHTARG = ltree[],
    COMMUTATOR = @,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@ (ltxtquery, ltree[]) OWNER TO postgres;

--
-- Name: @; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @ (
    PROCEDURE = _ltxtq_exec,
    LEFTARG = ltree[],
    RIGHTARG = ltxtquery,
    COMMUTATOR = @,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@ (ltree[], ltxtquery) OWNER TO postgres;

--
-- Name: @>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @> (
    PROCEDURE = ltree_isparent,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = <@,
    RESTRICT = ltreeparentsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@> (ltree, ltree) OWNER TO postgres;

--
-- Name: @>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @> (
    PROCEDURE = _ltree_isparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree,
    COMMUTATOR = <@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@> (ltree[], ltree) OWNER TO postgres;

--
-- Name: @>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR @> (
    PROCEDURE = _ltree_r_risparent,
    LEFTARG = ltree,
    RIGHTARG = ltree[],
    COMMUTATOR = <@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@> (ltree, ltree[]) OWNER TO postgres;

--
-- Name: ^<@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^<@ (
    PROCEDURE = ltree_risparent,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = ^@>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^<@ (ltree, ltree) OWNER TO postgres;

--
-- Name: ^<@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^<@ (
    PROCEDURE = _ltree_r_isparent,
    LEFTARG = ltree,
    RIGHTARG = ltree[],
    COMMUTATOR = ^@>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^<@ (ltree, ltree[]) OWNER TO postgres;

--
-- Name: ^<@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^<@ (
    PROCEDURE = _ltree_risparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree,
    COMMUTATOR = ^@>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^<@ (ltree[], ltree) OWNER TO postgres;

--
-- Name: ^?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^? (
    PROCEDURE = lt_q_rregex,
    LEFTARG = lquery[],
    RIGHTARG = ltree,
    COMMUTATOR = ^?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^? (lquery[], ltree) OWNER TO postgres;

--
-- Name: ^?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^? (
    PROCEDURE = lt_q_regex,
    LEFTARG = ltree,
    RIGHTARG = lquery[],
    COMMUTATOR = ^?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^? (ltree, lquery[]) OWNER TO postgres;

--
-- Name: ^?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^? (
    PROCEDURE = _lt_q_rregex,
    LEFTARG = lquery[],
    RIGHTARG = ltree[],
    COMMUTATOR = ^?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^? (lquery[], ltree[]) OWNER TO postgres;

--
-- Name: ^?; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^? (
    PROCEDURE = _lt_q_regex,
    LEFTARG = ltree[],
    RIGHTARG = lquery[],
    COMMUTATOR = ^?,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^? (ltree[], lquery[]) OWNER TO postgres;

--
-- Name: ^@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@ (
    PROCEDURE = ltxtq_rexec,
    LEFTARG = ltxtquery,
    RIGHTARG = ltree,
    COMMUTATOR = ^@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@ (ltxtquery, ltree) OWNER TO postgres;

--
-- Name: ^@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@ (
    PROCEDURE = ltxtq_exec,
    LEFTARG = ltree,
    RIGHTARG = ltxtquery,
    COMMUTATOR = ^@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@ (ltree, ltxtquery) OWNER TO postgres;

--
-- Name: ^@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@ (
    PROCEDURE = _ltxtq_rexec,
    LEFTARG = ltxtquery,
    RIGHTARG = ltree[],
    COMMUTATOR = ^@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@ (ltxtquery, ltree[]) OWNER TO postgres;

--
-- Name: ^@; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@ (
    PROCEDURE = _ltxtq_exec,
    LEFTARG = ltree[],
    RIGHTARG = ltxtquery,
    COMMUTATOR = ^@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@ (ltree[], ltxtquery) OWNER TO postgres;

--
-- Name: ^@>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@> (
    PROCEDURE = ltree_isparent,
    LEFTARG = ltree,
    RIGHTARG = ltree,
    COMMUTATOR = ^<@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@> (ltree, ltree) OWNER TO postgres;

--
-- Name: ^@>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@> (
    PROCEDURE = _ltree_isparent,
    LEFTARG = ltree[],
    RIGHTARG = ltree,
    COMMUTATOR = ^<@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@> (ltree[], ltree) OWNER TO postgres;

--
-- Name: ^@>; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^@> (
    PROCEDURE = _ltree_r_risparent,
    LEFTARG = ltree,
    RIGHTARG = ltree[],
    COMMUTATOR = ^<@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^@> (ltree, ltree[]) OWNER TO postgres;

--
-- Name: ^~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^~ (
    PROCEDURE = ltq_rregex,
    LEFTARG = lquery,
    RIGHTARG = ltree,
    COMMUTATOR = ^~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^~ (lquery, ltree) OWNER TO postgres;

--
-- Name: ^~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^~ (
    PROCEDURE = ltq_regex,
    LEFTARG = ltree,
    RIGHTARG = lquery,
    COMMUTATOR = ^~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^~ (ltree, lquery) OWNER TO postgres;

--
-- Name: ^~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^~ (
    PROCEDURE = _ltq_rregex,
    LEFTARG = lquery,
    RIGHTARG = ltree[],
    COMMUTATOR = ^~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^~ (lquery, ltree[]) OWNER TO postgres;

--
-- Name: ^~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ^~ (
    PROCEDURE = _ltq_regex,
    LEFTARG = ltree[],
    RIGHTARG = lquery,
    COMMUTATOR = ^~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.^~ (ltree[], lquery) OWNER TO postgres;

--
-- Name: ||; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR || (
    PROCEDURE = ltree_addltree,
    LEFTARG = ltree,
    RIGHTARG = ltree
);


ALTER OPERATOR public.|| (ltree, ltree) OWNER TO postgres;

--
-- Name: ||; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR || (
    PROCEDURE = ltree_addtext,
    LEFTARG = ltree,
    RIGHTARG = text
);


ALTER OPERATOR public.|| (ltree, text) OWNER TO postgres;

--
-- Name: ||; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR || (
    PROCEDURE = ltree_textadd,
    LEFTARG = text,
    RIGHTARG = ltree
);


ALTER OPERATOR public.|| (text, ltree) OWNER TO postgres;

--
-- Name: ~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ~ (
    PROCEDURE = ltq_rregex,
    LEFTARG = lquery,
    RIGHTARG = ltree,
    COMMUTATOR = ~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~ (lquery, ltree) OWNER TO postgres;

--
-- Name: ~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ~ (
    PROCEDURE = ltq_regex,
    LEFTARG = ltree,
    RIGHTARG = lquery,
    COMMUTATOR = ~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~ (ltree, lquery) OWNER TO postgres;

--
-- Name: ~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ~ (
    PROCEDURE = _ltq_rregex,
    LEFTARG = lquery,
    RIGHTARG = ltree[],
    COMMUTATOR = ~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~ (lquery, ltree[]) OWNER TO postgres;

--
-- Name: ~; Type: OPERATOR; Schema: public; Owner: postgres
--

CREATE OPERATOR ~ (
    PROCEDURE = _ltq_regex,
    LEFTARG = ltree[],
    RIGHTARG = lquery,
    COMMUTATOR = ~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~ (ltree[], lquery) OWNER TO postgres;

--
-- Name: gist__ltree_ops; Type: OPERATOR CLASS; Schema: public; Owner: postgres
--

CREATE OPERATOR CLASS gist__ltree_ops
    DEFAULT FOR TYPE ltree[] USING gist AS
    STORAGE ltree_gist ,
    OPERATOR 10 <@(ltree[],ltree) RECHECK ,
    OPERATOR 11 @>(ltree,ltree[]) RECHECK ,
    OPERATOR 12 ~(ltree[],lquery) RECHECK ,
    OPERATOR 13 ~(lquery,ltree[]) RECHECK ,
    OPERATOR 14 @(ltree[],ltxtquery) RECHECK ,
    OPERATOR 15 @(ltxtquery,ltree[]) RECHECK ,
    OPERATOR 16 ?(ltree[],lquery[]) RECHECK ,
    OPERATOR 17 ?(lquery[],ltree[]) RECHECK ,
    FUNCTION 1 _ltree_consistent(internal,internal,smallint) ,
    FUNCTION 2 _ltree_union(internal,internal) ,
    FUNCTION 3 _ltree_compress(internal) ,
    FUNCTION 4 ltree_decompress(internal) ,
    FUNCTION 5 _ltree_penalty(internal,internal,internal) ,
    FUNCTION 6 _ltree_picksplit(internal,internal) ,
    FUNCTION 7 _ltree_same(internal,internal,internal);


ALTER OPERATOR CLASS public.gist__ltree_ops USING gist OWNER TO postgres;

--
-- Name: gist_ltree_ops; Type: OPERATOR CLASS; Schema: public; Owner: postgres
--

CREATE OPERATOR CLASS gist_ltree_ops
    DEFAULT FOR TYPE ltree USING gist AS
    STORAGE ltree_gist ,
    OPERATOR 1 <(ltree,ltree) ,
    OPERATOR 2 <=(ltree,ltree) ,
    OPERATOR 3 =(ltree,ltree) ,
    OPERATOR 4 >=(ltree,ltree) ,
    OPERATOR 5 >(ltree,ltree) ,
    OPERATOR 10 @>(ltree,ltree) ,
    OPERATOR 11 <@(ltree,ltree) ,
    OPERATOR 12 ~(ltree,lquery) ,
    OPERATOR 13 ~(lquery,ltree) ,
    OPERATOR 14 @(ltree,ltxtquery) ,
    OPERATOR 15 @(ltxtquery,ltree) ,
    OPERATOR 16 ?(ltree,lquery[]) ,
    OPERATOR 17 ?(lquery[],ltree) ,
    FUNCTION 1 ltree_consistent(internal,internal,smallint) ,
    FUNCTION 2 ltree_union(internal,internal) ,
    FUNCTION 3 ltree_compress(internal) ,
    FUNCTION 4 ltree_decompress(internal) ,
    FUNCTION 5 ltree_penalty(internal,internal,internal) ,
    FUNCTION 6 ltree_picksplit(internal,internal) ,
    FUNCTION 7 ltree_same(internal,internal,internal);


ALTER OPERATOR CLASS public.gist_ltree_ops USING gist OWNER TO postgres;

--
-- Name: ltree_ops; Type: OPERATOR CLASS; Schema: public; Owner: postgres
--

CREATE OPERATOR CLASS ltree_ops
    DEFAULT FOR TYPE ltree USING btree AS
    OPERATOR 1 <(ltree,ltree) ,
    OPERATOR 2 <=(ltree,ltree) ,
    OPERATOR 3 =(ltree,ltree) ,
    OPERATOR 4 >=(ltree,ltree) ,
    OPERATOR 5 >(ltree,ltree) ,
    FUNCTION 1 ltree_cmp(ltree,ltree);


ALTER OPERATOR CLASS public.ltree_ops USING btree OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: acknowledged_duplicates; Type: TABLE; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE TABLE acknowledged_duplicates (
    md5 text NOT NULL
);


ALTER TABLE public.acknowledged_duplicates OWNER TO filemeta;

--
-- Name: TABLE acknowledged_duplicates; Type: COMMENT; Schema: public; Owner: filemeta
--

COMMENT ON TABLE acknowledged_duplicates IS 'Contains a list of all md5sums that should not be listed in the duplicates';


--
-- Name: node; Type: TABLE; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE TABLE node (
    uri text NOT NULL,
    path ltree,
    md5 character(32),
    mimetype character varying(48),
    created timestamp without time zone,
    updated timestamp without time zone,
    to_purge boolean DEFAULT false,
    rating integer DEFAULT 0
);


ALTER TABLE public.node OWNER TO filemeta;

--
-- Name: node_has_tag; Type: TABLE; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE TABLE node_has_tag (
    uri text NOT NULL,
    tag text NOT NULL
);


ALTER TABLE public.node_has_tag OWNER TO filemeta;

--
-- Name: query; Type: TABLE; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE TABLE query (
    query text NOT NULL,
    label text
);


ALTER TABLE public.query OWNER TO filemeta;

--
-- Name: tag; Type: TABLE; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE TABLE tag (
    name text NOT NULL
);


ALTER TABLE public.tag OWNER TO filemeta;

--
-- Name: acknowledged_duplicates_pkey; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY acknowledged_duplicates
    ADD CONSTRAINT acknowledged_duplicates_pkey PRIMARY KEY (md5);


--
-- Name: node_has_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY node_has_tag
    ADD CONSTRAINT node_has_tag_pkey PRIMARY KEY (uri, tag);


--
-- Name: node_pkey; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY node
    ADD CONSTRAINT node_pkey PRIMARY KEY (uri);


--
-- Name: query_pkey; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY query
    ADD CONSTRAINT query_pkey PRIMARY KEY (query);


--
-- Name: tag_pkey; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (name);


--
-- Name: unique_uri; Type: CONSTRAINT; Schema: public; Owner: filemeta; Tablespace: 
--

ALTER TABLE ONLY node
    ADD CONSTRAINT unique_uri UNIQUE (uri);


--
-- Name: node_path; Type: INDEX; Schema: public; Owner: filemeta; Tablespace: 
--

CREATE UNIQUE INDEX node_path ON node USING btree (path);


--
-- Name: node_has_tag_tag_fkey; Type: FK CONSTRAINT; Schema: public; Owner: filemeta
--

ALTER TABLE ONLY node_has_tag
    ADD CONSTRAINT node_has_tag_tag_fkey FOREIGN KEY (tag) REFERENCES tag(name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: node_has_tag_uri_fkey; Type: FK CONSTRAINT; Schema: public; Owner: filemeta
--

ALTER TABLE ONLY node_has_tag
    ADD CONSTRAINT node_has_tag_uri_fkey FOREIGN KEY (uri) REFERENCES node(uri) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

