package com.qunar.hotel.search.core.index;

import java.io.IOException;

import org.apache.lucene.search.suggest.fst.FSTCompletion;
import org.apache.lucene.search.suggest.fst.FSTCompletionBuilder;
import org.apache.lucene.util.BytesRef;

/**
 * @author hotel-search
 * @version 1.0
 *
 * @description For build hotel prefix index using FST.
 */
public class HotelPrefixIndexBuilder {

    FSTCompletionBuilder internalBuilder = new FSTCompletionBuilder();

    public void add(String surface, int weight) throws IOException {
        internalBuilder.add(new BytesRef(surface), weight);
    }

    public FSTCompletion build() throws IOException {
        return internalBuilder.build();
    }
} 