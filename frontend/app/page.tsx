import React from 'react'
import Head from 'next/head'
import dynamic from 'next/dynamic'

const Map = dynamic(() => import('../components/Map'), { ssr: false })

export default function Home() {
  return (
    <>
      <Head>
        <title>Property Search - Bangalore</title>
        <meta name="description" content="Property Search Map" />
      </Head>
      <main>
        <h1 style={{ textAlign: 'center' }}>Property Search - Bangalore</h1>
        <div style={{ height: '80vh', width: '100%' }}>
          <Map />
        </div>
      </main>
    </>
  )
}
