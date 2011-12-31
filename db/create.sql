SET client_min_messages = warning;

CREATE TABLE acknowledged_duplicates (
    md5 text NOT NULL PRIMARY KEY
);
COMMENT ON TABLE acknowledged_duplicates IS 'Contains a list of all md5sums that should not be listed in the duplicates';
ALTER TABLE acknowledged_duplicates OWNER TO filemeta;

CREATE TABLE node (
    md5 character(32) NOT NULL PRIMARY KEY,
    mimetype character varying(48),
    metadata hstore,
    created timestamp without time zone,
    updated timestamp without time zone
);
ALTER TABLE node OWNER TO filemeta;

CREATE TABLE file(
    md5 character(32) NOT NULL REFERENCES node(md5) ON UPDATE CASCADE ON DELETE CASCADE,
    path ltree UNIQUE,
    filepath text NOT NULL UNIQUE,
    PRIMARY KEY (md5, filepath)
);
ALTER TABLE file OWNER TO filemeta;

CREATE TABLE query (
    query text NOT NULL PRIMARY KEY,
    label text
);
ALTER TABLE query OWNER TO filemeta;

CREATE TABLE tag (
    name text NOT NULL PRIMARY KEY
);
ALTER TABLE tag OWNER TO filemeta;

CREATE TABLE tag_group (
    name text NOT NULL PRIMARY KEY
);
ALTER TABLE tag_group OWNER TO filemeta;

CREATE TABLE tag_in_tag_group (
    tagname text NOT NULL REFERENCES tag(name) ON UPDATE CASCADE ON DELETE CASCADE,
    groupname text NOT NULL REFERENCES tag_group(name) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (tagname, groupname)
);
ALTER TABLE tag_in_tag_group OWNER TO filemeta;

CREATE TABLE node_has_tag (
    md5 character(32) NOT NULL REFERENCES node(md5) ON UPDATE CASCADE ON DELETE CASCADE,
    tag text NOT NULL REFERENCES tag(name) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (md5, tag)
);
ALTER TABLE node_has_tag OWNER TO filemeta;

